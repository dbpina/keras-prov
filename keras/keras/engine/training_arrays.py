"""Part of the training engine related to plain array data (e.g. Numpy).
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
from scipy.sparse import issparse

from .training_utils import batch_shuffle
from .training_utils import check_num_samples
from .training_utils import make_batches
from .training_utils import should_run_validation
from .. import backend as K
from .. import callbacks as cbks
from ..utils.generic_utils import Progbar
from ..utils.generic_utils import slice_arrays
from ..utils.generic_utils import to_list
from ..utils.generic_utils import unpack_singleton

from dfa_lib_python.dataflow import Dataflow
from dfa_lib_python.transformation import Transformation
from dfa_lib_python.attribute import Attribute
from dfa_lib_python.attribute_type import AttributeType
from dfa_lib_python.set import Set
from dfa_lib_python.set_type import SetType
from dfa_lib_python.task import Task
from dfa_lib_python.dataset import DataSet
from dfa_lib_python.element import Element
from dfa_lib_python.task_status import TaskStatus
import time


def fit_loop(model, fit_function, fit_inputs,
             out_labels=None,
             batch_size=None,
             epochs=100,
             verbose=1,
             callbacks=None,
             val_function=None,
             val_inputs=None,
             shuffle=True,
             initial_epoch=0,
             steps_per_epoch=None,
             validation_steps=None,
             validation_freq=1):
    """Abstract fit function for `fit_function(fit_inputs)`.

    Assumes that fit_function returns a list, labeled by out_labels.

    # Arguments
        model: Keras model instance.
        fit_function: Keras function returning a list of tensors
        fit_inputs: List of tensors to be fed to `fit_function`
        out_labels: List of strings, display names of
            the outputs of `fit_function`
        batch_size: Integer batch size or None if unknown.
        epochs: Number of times to iterate over the data
        verbose: Verbosity mode, 0, 1 or 2
        callbacks: List of callbacks to be called during training and validation
            (if `val_function` and `val_inputs` are not `None`).
        val_function: Keras function to call for validation
        val_inputs: List of tensors to be fed to `val_function`
        shuffle: Whether to shuffle the data at the beginning of each epoch
        initial_epoch: Epoch at which to start training
            (useful for resuming a previous training run)
        steps_per_epoch: Total number of steps (batches of samples)
            before declaring one epoch finished and starting the
            next epoch. Ignored with the default value of `None`.
        validation_steps: Number of steps to run validation for
            (only if doing validation from data tensors).
            Ignored with the default value of `None`.
        validation_freq: Only relevant if validation data is provided. Integer
            or list/tuple/set. If an integer, specifies how many training
            epochs to run before a new validation run is performed, e.g.
            validation_freq=2` runs validation every 2 epochs. If a list,
            tuple, or set, specifies the epochs on which to run validation,
            e.g. `validation_freq=[1, 2, 10]` runs validation at the end
            of the 1st, 2nd, and 10th epochs.

    # Returns
        `History` object.
    """
    do_validation = False
    if val_function and val_inputs:
        do_validation = True
        if (verbose and fit_inputs and
           hasattr(fit_inputs[0], 'shape') and hasattr(val_inputs[0], 'shape')):
            print('Train on %d samples, validate on %d samples' %
                  (fit_inputs[0].shape[0], val_inputs[0].shape[0]))
    if validation_steps:
        do_validation = True
        if steps_per_epoch is None:
            raise ValueError('Can only use `validation_steps` '
                             'when doing step-wise '
                             'training, i.e. `steps_per_epoch` '
                             'must be set.')
    elif do_validation:
        if steps_per_epoch:
            raise ValueError('Must specify `validation_steps` '
                             'to perform validation '
                             'when doing step-wise training.')

    num_train_samples = check_num_samples(fit_inputs,
                                          batch_size=batch_size,
                                          steps=steps_per_epoch,
                                          steps_name='steps_per_epoch')
    if num_train_samples is not None:
        index_array = np.arange(num_train_samples)

    model.history = cbks.History()
    _callbacks = [cbks.BaseLogger(stateful_metrics=model.metrics_names[1:])]
    if verbose:
        if steps_per_epoch is not None:
            count_mode = 'steps'
        else:
            count_mode = 'samples'
        _callbacks.append(
            cbks.ProgbarLogger(count_mode, stateful_metrics=model.metrics_names[1:]))
    _callbacks += (callbacks or []) + [model.history]
    callbacks = cbks.CallbackList(_callbacks)
    out_labels = out_labels or []

    # it's possible to callback a different model than itself
    # (used by Sequential models)
    callback_model = model._get_callback_model()
    callback_metrics = list(model.metrics_names)
    if do_validation:
        callback_metrics += ['val_' + n for n in model.metrics_names]

    callbacks.set_model(callback_model)
    callbacks.set_params({
        'batch_size': batch_size,
        'epochs': epochs,
        'steps': steps_per_epoch,
        'samples': num_train_samples,
        'verbose': verbose,
        'do_validation': do_validation,
        'metrics': callback_metrics,
    })
    callbacks._call_begin_hook('train')
    callbacks.model.stop_training = False
    for cbk in callbacks:
        cbk.validation_data = val_inputs

    # To prevent a slowdown,
    # we find beforehand the arrays that need conversion.
    feed = (model._feed_inputs +
            model._feed_targets +
            model._feed_sample_weights)
    indices_for_conversion_to_dense = []
    for i in range(len(feed)):
        if issparse(fit_inputs[i]) and not K.is_sparse(feed[i]):
            indices_for_conversion_to_dense.append(i)

    if (model.capture_provenance):

        training_id = ""
        if "TrainingModel" in model.transformations_task:
            training_id = model.transformations_task["TrainingModel"]
        elif "trainingmodel" in model.transformations_task:
            training_id = model.transformations_task["trainingmodel"]

        t1 = Task(1, model.dataflow_tag, model.exec_tag, "TrainingModel")    
        t1.begin()        

        if('momentum' in model.optimizer.get_config()):
            momentum = model.optimizer.get_config()['momentum']
        else:
            momentum = 0

        if('decay' in model.optimizer.get_config()):
            decay = model.optimizer.get_config()['decay']
        else:
            decay = 0
        
        hyps_values = {"OPTIMIZER_NAME": model.optimizer.__class__.__name__,
                "LEARNING_RATE": round(model.optimizer.get_config()['learning_rate'], 7),
                "DECAY": decay,
                "MOMENTUM": momentum,
                "NUM_EPOCHS": epochs,
                "BATCH_SIZE": batch_size,
                "NUM_LAYERS": len(model.layers)}

        # t3 = Task(2, model.dataflow_tag, "Layers")
        # t3.begin()


        count = 0
        time_now = time.time()
        for layer in model.layers:
            layer_data = []
            count = count + 1
            if "activation" in layer.get_config()['name']:
                layer_data.append(time_now)
                layer_data.append(layer.get_config()['name'])
                layer_data.append("activation")
                layer_data.append(layer.get_config()['activation'])
                t3_input= DataSet("iLayers", [Element(layer_data)])
                t1.add_dataset(t3_input)
                # if count < len(model.layers):
                t1.save()

            elif "dropout" in layer.get_config()['name']:
                layer_data.append(time_now)
                layer_data.append(layer.get_config()['name'])
                layer_data.append("dropout")
                layer_data.append(layer.get_config()['rate'])
                t3_input= DataSet("iLayers", [Element(layer_data)])
                t1.add_dataset(t3_input)
                # if count < len(model.layers):
                t1.save()    

        values_to_store = []
        values_to_store.append(time_now)
        if (bool(model.final_hyperparameters)):
            for i in model.final_hyperparameters:
                if (i.upper() in hyps_values): 
                    values_to_store.append(hyps_values[i.upper()])
                else: 
                    values_to_store.append("null")
            t1_input = DataSet("iTrainingModel", [Element(values_to_store)])
            t1.add_dataset(t1_input)  
            t1.save()


    for epoch in range(initial_epoch, epochs):
        start = time.time()
        model.reset_metrics()
        callbacks.on_epoch_begin(epoch)
        epoch_logs = {}
        if steps_per_epoch is not None:
            for step_index in range(steps_per_epoch):
                batch_logs = {'batch': step_index, 'size': 1}
                callbacks._call_batch_hook('train', 'begin', step_index, batch_logs)
                outs = fit_function(fit_inputs)

                outs = to_list(outs)
                for l, o in zip(out_labels, outs):
                    batch_logs[l] = o

                callbacks._call_batch_hook('train', 'end', step_index, batch_logs)
                if callback_model.stop_training:
                    break

            if do_validation and should_run_validation(validation_freq, epoch):
                val_outs = test_loop(model, val_function, val_inputs,
                                     steps=validation_steps,
                                     callbacks=callbacks,
                                     verbose=0,
                                     type="train")
                val_outs = to_list(val_outs)
                # Same labels assumed.
                for l, o in zip(out_labels, val_outs):
                    epoch_logs['val_' + l] = o
        else:
            if shuffle == 'batch':
                index_array = batch_shuffle(index_array, batch_size)
            elif shuffle:
                np.random.shuffle(index_array)

            batches = make_batches(num_train_samples, batch_size)
            for batch_index, (batch_start, batch_end) in enumerate(batches):
                batch_ids = index_array[batch_start:batch_end]
                try:
                    if isinstance(fit_inputs[-1], int):
                        # Do not slice the training phase flag.
                        ins_batch = slice_arrays(
                            fit_inputs[:-1], batch_ids) + [fit_inputs[-1]]
                    else:
                        ins_batch = slice_arrays(fit_inputs, batch_ids)
                except TypeError:
                    raise TypeError('TypeError while preparing batch. '
                                    'If using HDF5 input data, '
                                    'pass shuffle="batch".')
                batch_logs = {'batch': batch_index, 'size': len(batch_ids)}
                callbacks._call_batch_hook('train', 'begin', batch_index, batch_logs)
                for i in indices_for_conversion_to_dense:
                    ins_batch[i] = ins_batch[i].toarray()

                outs = fit_function(ins_batch)
                outs = to_list(outs)
                for l, o in zip(out_labels, outs):
                    batch_logs[l] = o

                callbacks._call_batch_hook('train', 'end', batch_index, batch_logs)
                if callbacks.model.stop_training:
                    break

            if batch_index == len(batches) - 1:  # Last batch.
                if do_validation and should_run_validation(validation_freq, epoch):
                    val_outs = test_loop(model, val_function, val_inputs,
                                         batch_size=batch_size,
                                         callbacks=callbacks,
                                         verbose=0,
                                         type="train")
                    val_outs = to_list(val_outs)
                    # Same labels assumed.
                    for l, o in zip(out_labels, val_outs):
                        epoch_logs['val_' + l] = o

        callbacks.on_epoch_end(epoch, epoch_logs)

        if callbacks.model.stop_training:
            break
        if model.capture_provenance is True:
            now = time.time()           
            m_values = []
            m_values.append(now)
            m_values.append(now - start)
            m_values.append(epoch)
            for i in callback_metrics:
                if np.isnan(epoch_logs[i]):
                    epoch_logs[i] = -9999999
                m_values.append(epoch_logs[i])

            t1_output = DataSet("oTrainingModel", [Element(m_values)])

            t1.add_dataset(t1_output)
            if(epoch==epochs-1):
                t1.end()
            else:
                epoch = epoch + 1
                t1.save()    
    callbacks._call_end_hook('train')
    return model.history


def predict_loop(model, f, ins,
                 batch_size=32,
                 verbose=0,
                 steps=None,
                 callbacks=None):
    """Abstract method to loop over some data in batches.

    # Arguments
        model: Keras model instance.
        f: Keras function returning a list of tensors.
        ins: list of tensors to be fed to `f`.
        batch_size: integer batch size.
        verbose: verbosity mode.
        steps: Total number of steps (batches of samples)
            before declaring `predict_loop` finished.
            Ignored with the default value of `None`.
        callbacks: List of callbacks or an instance of
            `keras.callbacks.CallbackList` to be called during prediction.

    # Returns
        Array of predictions (if the model has a single output)
        or list of arrays of predictions
        (if the model has multiple outputs).
    """
    num_samples = check_num_samples(ins,
                                    batch_size=batch_size,
                                    steps=steps,
                                    steps_name='steps')

    # Check if callbacks have not been already configured
    if not isinstance(callbacks, cbks.CallbackList):
        callbacks = cbks.CallbackList(callbacks)
        callback_model = model._get_callback_model()
        callbacks.set_model(callback_model)
        callback_params = {
            'batch_size': batch_size,
            'steps': steps,
            'samples': num_samples,
            'verbose': verbose,
        }
        callbacks.set_params(callback_params)

    if verbose == 1:
        if steps is not None:
            progbar = Progbar(target=steps)
        else:
            progbar = Progbar(target=num_samples)

    indices_for_conversion_to_dense = []
    for i in range(len(model._feed_inputs)):
        if issparse(ins[i]) and not K.is_sparse(model._feed_inputs[i]):
            indices_for_conversion_to_dense.append(i)

    callbacks.model.stop_training = False
    callbacks._call_begin_hook('predict')

    if steps is not None:
        # Step-based predictions.
        # Since we do not know how many samples
        # we will see, we cannot pre-allocate
        # the returned Numpy arrays.
        # Instead, we store one array per batch seen
        # and concatenate them upon returning.
        unconcatenated_outs = []
        for step in range(steps):
            batch_logs = {'batch': step, 'size': 1}
            callbacks._call_batch_hook('predict', 'begin', step, batch_logs)
            batch_outs = f(ins)
            batch_outs = to_list(batch_outs)
            if step == 0:
                for batch_out in batch_outs:
                    unconcatenated_outs.append([])
            for i, batch_out in enumerate(batch_outs):
                unconcatenated_outs[i].append(batch_out)

            batch_logs['outputs'] = batch_outs
            callbacks._call_batch_hook('predict', 'end', step, batch_logs)
            if verbose == 1:
                progbar.update(step + 1)
        callbacks.on_predict_end()
        if len(unconcatenated_outs) == 1:
            return np.concatenate(unconcatenated_outs[0], axis=0)
        return [np.concatenate(unconcatenated_outs[i], axis=0)
                for i in range(len(unconcatenated_outs))]
    else:
        # Sample-based predictions.
        outs = []
        batches = make_batches(num_samples, batch_size)
        index_array = np.arange(num_samples)
        for batch_index, (batch_start, batch_end) in enumerate(batches):
            batch_ids = index_array[batch_start:batch_end]
            if ins and isinstance(ins[-1], int):
                # Do not slice the training phase flag.
                ins_batch = slice_arrays(ins[:-1], batch_ids) + [ins[-1]]
            else:
                ins_batch = slice_arrays(ins, batch_ids)
            for i in indices_for_conversion_to_dense:
                ins_batch[i] = ins_batch[i].toarray()

            batch_logs = {'batch': batch_index, 'size': len(batch_ids)}
            callbacks._call_batch_hook('predict', 'begin', batch_index, batch_logs)
            batch_outs = f(ins_batch)
            batch_outs = to_list(batch_outs)
            if batch_index == 0:
                # Pre-allocate the results arrays.
                for batch_out in batch_outs:
                    shape = (num_samples,) + batch_out.shape[1:]
                    outs.append(np.zeros(shape, dtype=batch_out.dtype))
            for i, batch_out in enumerate(batch_outs):
                outs[i][batch_start:batch_end] = batch_out

            batch_logs['outputs'] = batch_outs
            callbacks._call_batch_hook('predict', 'end', batch_index, batch_logs)
            if verbose == 1:
                progbar.update(batch_end)
        callbacks._call_end_hook('predict')
        return unpack_singleton(outs)


def test_loop(model, f, ins,
              batch_size=None,
              verbose=0,
              steps=None,
              callbacks=None,
              type=None):
    """Abstract method to loop over some data in batches.

    # Arguments
        model: Keras model instance.
        f: Keras function returning a list of tensors.
        ins: list of tensors to be fed to `f`.
        batch_size: integer batch size or `None`.
        verbose: verbosity mode.
        steps: Total number of steps (batches of samples)
            before declaring predictions finished.
            Ignored with the default value of `None`.
        callbacks: List of callbacks or an instance of
            `keras.callbacks.CallbackList` to be called during evaluation.

    # Returns
        Scalar loss (if the model has a single output and no metrics)
        or list of scalars (if the model has multiple outputs
        and/or metrics). The attribute `model.metrics_names` will give you
        the display labels for the scalar outputs.
    """

    model.reset_metrics()
    num_samples = check_num_samples(ins,
                                    batch_size=batch_size,
                                    steps=steps,
                                    steps_name='steps')

    # Check if callbacks have not been already configured
    if not isinstance(callbacks, cbks.CallbackList):
        callbacks = cbks.CallbackList(callbacks)
        callback_model = model._get_callback_model()
        callbacks.set_model(callback_model)
        callback_metrics = list(model.metrics_names)
        callback_params = {
            'batch_size': batch_size,
            'steps': steps,
            'samples': num_samples,
            'verbose': verbose,
            'metrics': callback_metrics,
        }
        callbacks.set_params(callback_params)

    outs = []
    if verbose == 1:
        if steps is not None:
            progbar = Progbar(target=steps)
        else:
            progbar = Progbar(target=num_samples)

    # To prevent a slowdown,
    # we find beforehand the arrays that need conversion.
    feed = (model._feed_inputs +
            model._feed_targets +
            model._feed_sample_weights)
    indices_for_conversion_to_dense = []
    for i in range(len(feed)):
        if issparse(ins[i]) and not K.is_sparse(feed[i]):
            indices_for_conversion_to_dense.append(i)

    callbacks.model.stop_training = False
    callbacks._call_begin_hook('test')

    if steps is not None:
        for step in range(steps):
            batch_logs = {'batch': step, 'size': 1}
            callbacks._call_batch_hook('test', 'begin', step, batch_logs)
            batch_outs = f(ins)
            if isinstance(batch_outs, list):
                if step == 0:
                    outs.extend([0.] * len(batch_outs))
                for i, batch_out in enumerate(batch_outs):
                    if i == 0:  # Index 0 == `Loss`
                        outs[i] = float(batch_out)
                    else:
                        outs[i] += float(batch_out)
            else:
                if step == 0:
                    outs.append(0.)
                outs[0] += float(batch_outs)

            for l, o in zip(model.metrics_names, batch_outs):
                batch_logs[l] = o
            callbacks._call_batch_hook('test', 'end', step, batch_logs)

            if verbose == 1:
                progbar.update(step + 1)
        outs[0] /= steps  # Index 0 == `Loss`
    else:
        batches = make_batches(num_samples, batch_size)
        index_array = np.arange(num_samples)
        for batch_index, (batch_start, batch_end) in enumerate(batches):
            batch_ids = index_array[batch_start:batch_end]
            if isinstance(ins[-1], int):
                # Do not slice the training phase flag.
                ins_batch = slice_arrays(ins[:-1], batch_ids) + [ins[-1]]
            else:
                ins_batch = slice_arrays(ins, batch_ids)
            for i in indices_for_conversion_to_dense:
                ins_batch[i] = ins_batch[i].toarray()

            batch_logs = {'batch': batch_index, 'size': len(batch_ids)}
            callbacks._call_batch_hook('test', 'begin', batch_index, batch_logs)
            batch_outs = f(ins_batch)
            if isinstance(batch_outs, list):
                if batch_index == 0:
                    outs.extend([0.] * len(batch_outs))
                for i, batch_out in enumerate(batch_outs):
                    if i == 0:  # Index 0 == `Loss`
                        outs[i] += float(batch_out) * len(batch_ids)
                    else:
                        outs[i] = float(batch_out)
            else:
                if batch_index == 0:
                    outs.append(0.)
                outs[0] += float(batch_outs) * len(batch_ids)

            for l, o in zip(model.metrics_names, batch_outs):
                batch_logs[l] = float(o)
            callbacks._call_batch_hook('test', 'end', batch_index, batch_logs)

            if verbose == 1:
                progbar.update(batch_end)
        outs[0] /= num_samples  # Index 0 == `Loss`
    callbacks._call_end_hook('test')

    if model.capture_provenance is True:
        if type == "evaluate":
            t11 = Task(1, model.dataflow_tag, model.exec_tag, "TrainingModel") 
            t3 = Task(3, model.dataflow_tag, model.exec_tag, "TestingModel", dependency=t11)     
            t3.begin()                
            now = time.time()
            t_values = []
            t_values.append(now)
            if steps is not None:
                #print("outs")
                #print(outs)
                for i in model.metrics_names:
                    if np.isnan(outs[i]):
                        outs[i] = -9999999
                    t_values.append(outs[i])
            else:
                #print("batch")
                #print(batch_logs)
                #print(batch_logs['loss'])
                #print(outs[0])
                for i in model.metrics_names:
                    if np.isnan(batch_logs[i]):
                        batch_logs[i] = -9999999
                    t_values.append(batch_logs[i])
            testing_output = DataSet("oTestingModel", [Element(t_values)])
            t3.add_dataset(testing_output)
            t3.end()
       
    return unpack_singleton(outs)
