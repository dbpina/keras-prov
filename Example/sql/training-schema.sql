START TRANSACTION;


-- sequences
CREATE SEQUENCE "df_id_seq" as integer START WITH 1;
CREATE SEQUENCE "version_id_seq" as integer START WITH 1;
CREATE SEQUENCE "dt_id_seq" as integer START WITH 1;
CREATE SEQUENCE "program_id_seq" as integer START WITH 1;
CREATE SEQUENCE "ds_id_seq" as integer START WITH 1;
CREATE SEQUENCE "dd_id_seq" as integer START WITH 1;
CREATE SEQUENCE "extractor_id_seq" as integer START WITH 1;
CREATE SEQUENCE "ecombination_id_seq" as integer START WITH 1;
CREATE SEQUENCE "att_id_seq" as integer START WITH 1;
CREATE SEQUENCE "task_id_seq" as integer START WITH 1;
CREATE SEQUENCE "file_id_seq" as integer START WITH 1;
CREATE SEQUENCE "performance_id_seq" as integer START WITH 1;

CREATE SEQUENCE "ifilters_id_seq" AS INTEGER;
CREATE SEQUENCE "ilayers_id_seq" AS INTEGER;
CREATE SEQUENCE "itrainingmodel_id_seq" AS INTEGER;
CREATE SEQUENCE "oadaptation_id_seq" AS INTEGER;
CREATE SEQUENCE "ofilters_id_seq" AS INTEGER;
CREATE SEQUENCE "otestingmodel_id_seq" AS INTEGER;
CREATE SEQUENCE "otrainingmodel_id_seq" AS INTEGER;

--tables
CREATE TABLE dataflow(
        id INTEGER DEFAULT NEXT VALUE FOR "df_id_seq" NOT NULL,
        tag VARCHAR(50) NOT NULL,
        PRIMARY KEY ("id")
);

CREATE TABLE dataflow_version(
        version INTEGER DEFAULT NEXT VALUE FOR "version_id_seq" NOT NULL,
        df_id INTEGER NOT NULL,
        PRIMARY KEY ("version"),
        FOREIGN KEY ("df_id") REFERENCES dataflow("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE data_transformation(
        id INTEGER DEFAULT NEXT VALUE FOR "dt_id_seq" NOT NULL,
        df_id INTEGER NOT NULL,
        tag VARCHAR(50) NOT NULL,
        PRIMARY KEY ("id"),
        FOREIGN KEY ("df_id") REFERENCES dataflow("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE program(
        id INTEGER DEFAULT NEXT VALUE FOR "program_id_seq" NOT NULL,
        df_id INTEGER NOT NULL,
        name VARCHAR(200) NOT NULL,
        path VARCHAR(500) NOT NULL,
        PRIMARY KEY ("id"),
        FOREIGN KEY ("df_id") REFERENCES dataflow("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE use_program(
        dt_id INTEGER NOT NULL,
        program_id INTEGER NOT NULL,
        PRIMARY KEY ("dt_id","program_id"),
        FOREIGN KEY ("dt_id") REFERENCES data_transformation("id") ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY ("program_id") REFERENCES program("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE data_set(
        id INTEGER DEFAULT NEXT VALUE FOR "ds_id_seq" NOT NULL,
        df_id INTEGER NOT NULL,
        tag VARCHAR(50) NOT NULL,
        PRIMARY KEY ("id"),
        FOREIGN KEY ("df_id") REFERENCES dataflow("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE data_dependency(
        id INTEGER DEFAULT NEXT VALUE FOR "dd_id_seq" NOT NULL,
        previous_dt_id INTEGER,
        next_dt_id INTEGER,
        ds_id INTEGER NOT NULL,
        PRIMARY KEY ("id"),
        FOREIGN KEY ("previous_dt_id") REFERENCES data_transformation("id") ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY ("next_dt_id") REFERENCES data_transformation("id") ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY ("ds_id") REFERENCES data_set("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE extractor(
        id INTEGER DEFAULT NEXT VALUE FOR "extractor_id_seq" NOT NULL,
        ds_id INTEGER NOT NULL,
        tag VARCHAR(20) NOT NULL,
        cartridge VARCHAR(20) NOT NULL,
        extension VARCHAR(20) NOT NULL,
        PRIMARY KEY ("id"),
        FOREIGN KEY ("ds_id") REFERENCES data_set("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE extractor_combination(
        id INTEGER DEFAULT NEXT VALUE FOR "ecombination_id_seq" NOT NULL,
        ds_id INTEGER NOT NULL,
        outer_ext_id INTEGER NOT NULL,
        inner_ext_id INTEGER NOT NULL,
        keys VARCHAR(100) NOT NULL,
        key_types VARCHAR(100) NOT NULL,
        PRIMARY KEY ("id"),
        FOREIGN KEY ("ds_id") REFERENCES data_set("id") ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY ("outer_ext_id") REFERENCES extractor("id") ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY ("inner_ext_id") REFERENCES extractor("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE attribute(
        id INTEGER DEFAULT NEXT VALUE FOR "att_id_seq" NOT NULL,
        ds_id INTEGER NOT NULL,
        extractor_id INTEGER,
        name VARCHAR(30),
        type VARCHAR(15),
        PRIMARY KEY ("id"),
        FOREIGN KEY ("ds_id") REFERENCES data_set("id") ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY ("extractor_id") REFERENCES extractor("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE task(
        id INTEGER DEFAULT NEXT VALUE FOR "task_id_seq" NOT NULL,
        identifier INTEGER NOT NULL,
        df_version INTEGER NOT NULL,
        dt_id INTEGER NOT NULL,
        status VARCHAR(10),
        workspace VARCHAR(500),
        computing_resource VARCHAR(100),
        output_msg TEXT,
        error_msg TEXT,
        PRIMARY KEY ("id"),
        FOREIGN KEY ("df_version") REFERENCES dataflow_version("version") ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY ("dt_id") REFERENCES data_transformation("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE file(
        id INTEGER DEFAULT NEXT VALUE FOR "file_id_seq" NOT NULL,
        task_id INTEGER NOT NULL,
        name VARCHAR(200) NOT NULL,
        path VARCHAR(500) NOT NULL,
        PRIMARY KEY ("id"),
        FOREIGN KEY ("task_id") REFERENCES task("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE performance(
        id INTEGER DEFAULT NEXT VALUE FOR "performance_id_seq" NOT NULL,
        task_id INTEGER NOT NULL,       
        subtask_id INTEGER,     
        method VARCHAR(30) NOT NULL,
        description VARCHAR(200),
        starttime VARCHAR(30),
        endtime VARCHAR(30),
        invocation TEXT,
        PRIMARY KEY ("id"),
        FOREIGN KEY ("task_id") REFERENCES task("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "ds_ifilters" (
        "id"              INTEGER       NOT NULL DEFAULT next value for "ifilters_id_seq",
        "filters_task_id" INTEGER,
        "timestamp"       VARCHAR(500),
        "dataset_name"    VARCHAR(500),
        CONSTRAINT "ds_ifilters_id_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "ds_ofilters" (
        "id"              INTEGER       NOT NULL DEFAULT next value for "ofilters_id_seq",
        "filters_task_id" INTEGER,
        "timestamp"       VARCHAR(500),
        "filter_name"     VARCHAR(500),
        CONSTRAINT "ds_ofilters_id_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "ds_ilayers" (
        "id"                    INTEGER       NOT NULL DEFAULT next value for "ilayers_id_seq",
        "trainingmodel_task_id" INTEGER,
        "timestamp"             VARCHAR(500),
        "name"                  VARCHAR(500),
        "attribute_type"        VARCHAR(500),
        "value"                 VARCHAR(500),
        CONSTRAINT "ds_ilayers_id_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "ds_itrainingmodel" (
        "id"                    INTEGER       NOT NULL DEFAULT next value for "itrainingmodel_id_seq",
        "trainingmodel_task_id" INTEGER,
        "timestamp"             VARCHAR(500),
        "optimizer_name"        VARCHAR(500),
        "learning_rate"         DOUBLE,
        "decay"                 DOUBLE,
        "momentum"              DOUBLE,
        "num_epochs"            DOUBLE,
        "batch_size"            DOUBLE,
        "num_layers"            DOUBLE,
        CONSTRAINT "ds_itrainingmodel_id_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "ds_otrainingmodel" (
        "id"                    INTEGER       NOT NULL DEFAULT next value for "otrainingmodel_id_seq",
        "trainingmodel_task_id" INTEGER,
        "adaptation_task_id"    INTEGER,
        "testingmodel_task_id"  INTEGER,
        "timestamp"             VARCHAR(500),
        "elapsed_time"          VARCHAR(500),
        "loss"                  DOUBLE,
        "accuracy"              DOUBLE,
        "val_loss"              DOUBLE,
        "val_accuracy"          DOUBLE,
        "epoch"                 DOUBLE,
        CONSTRAINT "ds_otrainingmodel_id_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "ds_oadaptation" (
        "id"                 INTEGER       NOT NULL DEFAULT next value for "oadaptation_id_seq",
        "adaptation_task_id" INTEGER,
        "new_lrate"          DOUBLE,
        "timestamp"          VARCHAR(500),
        "epoch_id"           DOUBLE,
        "adaptation_id"      DOUBLE,
        CONSTRAINT "ds_oadaptation_id_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "ds_otestingmodel" (
        "id"                   INTEGER       NOT NULL DEFAULT next value for "otestingmodel_id_seq",
        "testingmodel_task_id" INTEGER,
        "timestamp"            VARCHAR(500),
        "loss"                 DOUBLE,
        "accuracy"             DOUBLE,
        CONSTRAINT "ds_otestingmodel_id_pkey" PRIMARY KEY ("id")
);

--procedures
CREATE FUNCTION insertDataflow (v_tag VARCHAR(50))
RETURNS INTEGER
BEGIN
        DECLARE v_df_id INTEGER;
    SELECT df.id INTO v_df_id FROM dataflow df WHERE df.tag=v_tag;
    IF(v_df_id IS NULL) THEN
        #SELECT NEXT VALUE FOR "df_id_seq" into v_df_id;
        INSERT INTO dataflow(tag) VALUES (v_tag);
        END IF;
        RETURN SELECT df.id FROM dataflow df WHERE df.tag=v_tag;
END;

-- DROP FUNCTION insertDataflowVersion;
CREATE FUNCTION insertDataflowVersion (vdf_id INTEGER)
RETURNS INTEGER
BEGIN
        DECLARE version_id INTEGER;
        #SELECT NEXT VALUE FOR "version_id_seq" into version_id;
    INSERT INTO dataflow_version(df_id) VALUES (vdf_id);
        RETURN SELECT dfv.version FROM dataflow_version dfv WHERE dfv.df_id=vdf_id AND dfv.version=get_value_for('public', 'version_id_seq');
END;

-- DROP FUNCTION insertDataTransformation;
CREATE FUNCTION insertDataTransformation (vdf_id INTEGER, vtag VARCHAR(50))
RETURNS INTEGER
BEGIN
        DECLARE vdt_id INTEGER;
    SELECT id INTO vdt_id FROM data_transformation WHERE df_id = vdf_id AND tag = vtag;
    IF(vdt_id IS NULL) THEN
        #SELECT NEXT VALUE FOR "dt_id_seq" into vdt_id;
        INSERT INTO data_transformation(df_id,tag) VALUES (vdf_id,vtag);
        END IF;
        RETURN SELECT id FROM data_transformation WHERE df_id = vdf_id AND tag = vtag;
END;

-- DROP FUNCTION insertProgram;
CREATE FUNCTION insertProgram (vdf_id INTEGER, vdt_id INTEGER, vname VARCHAR(200), vpath VARCHAR(500))
RETURNS INTEGER
BEGIN
        DECLARE vprogram_id INTEGER;
    SELECT id INTO vprogram_id FROM program p WHERE df_id = vdf_id AND name = vname AND path = vpath;

    IF(vprogram_id IS NULL) THEN
        SELECT NEXT VALUE FOR "program_id_seq" into vprogram_id;
        INSERT INTO program(id,df_id,name,path) VALUES (vprogram_id,vdf_id,vname,vpath);
        END IF;
        INSERT INTO use_program(dt_id,program_id) VALUES (vdt_id,vprogram_id);
        RETURN vprogram_id;
END;

-- DROP FUNCTION insertDataSet;
CREATE FUNCTION insertDataSet (vdf_id INTEGER, vdt_id INTEGER, vdep_dt_id INTEGER, vtag VARCHAR(500), vtype VARCHAR(10))
RETURNS INTEGER
BEGIN
        DECLARE vds_id INTEGER;
    SELECT id INTO vds_id FROM data_set ds WHERE df_id = vdf_id AND tag = vtag;

    IF(vds_id IS NULL) THEN
        #SELECT NEXT VALUE FOR "ds_id_seq" into vds_id;
        INSERT INTO data_set(df_id,tag) VALUES (vdf_id,vtag);
        SELECT id INTO vds_id FROM data_set ds WHERE df_id = vdf_id AND tag = vtag;
        END IF;

        IF(vdep_dt_id IS NOT NULL) THEN
                DECLARE vdd_id INTEGER;
                SELECT ds_id INTO vdd_id FROM data_dependency
                WHERE previous_dt_id = vdep_dt_id AND next_dt_id = vdt_id AND ds_id = vds_id;

                DECLARE vid INTEGER;
                SELECT id INTO vid FROM data_dependency WHERE previous_dt_id = vdep_dt_id AND next_dt_id IS NULL;

                IF(vid IS NULL) THEN
                        IF(vdd_id IS NULL) THEN
                                DECLARE vdd_id INTEGER;
                                #SELECT NEXT VALUE FOR "dd_id_seq" into vdd_id;
                                INSERT INTO data_dependency(previous_dt_id,next_dt_id,ds_id) VALUES (vdep_dt_id,vdt_id,vds_id);
                        END IF;
                ELSE
                        UPDATE data_dependency SET next_dt_id = vdt_id WHERE id = vid;
                END IF;
        ELSE
                DECLARE vdd_id INTEGER;
                #SELECT NEXT VALUE FOR "dd_id_seq" into vdd_id;

                IF(vtype LIKE 'INPUT') THEN
                        INSERT INTO data_dependency(previous_dt_id,next_dt_id,ds_id) VALUES (null,vdt_id,vds_id);
                ELSE
                        INSERT INTO data_dependency(previous_dt_id,next_dt_id,ds_id) VALUES (vdt_id,null,vds_id);
                END IF;
        END IF;

        RETURN vds_id;
END;

-- DROP FUNCTION insertAttribute;
CREATE FUNCTION insertAttribute (dds_id INTEGER, vextractor_id INTEGER, vname VARCHAR(30), vtype VARCHAR(15))
RETURNS INTEGER
BEGIN
        DECLARE vid INTEGER;
    SELECT id INTO vid FROM attribute WHERE ds_id=dds_id AND name=vname;
    IF(vid IS NULL) THEN
        #SELECT NEXT VALUE FOR "att_id_seq" into vid;
        INSERT INTO attribute(ds_id,extractor_id,name,type) VALUES (dds_id,vextractor_id,vname,vtype);
        END IF;
        RETURN SELECT id FROM attribute WHERE ds_id=dds_id AND name=vname;
END;

-- DROP FUNCTION insertTask;
CREATE FUNCTION insertTask (videntifier INTEGER, vdf_tag VARCHAR(50), vdt_tag VARCHAR(50), vstatus VARCHAR(10), vworkspace VARCHAR(500), 
        vcomputing_resource VARCHAR(100), voutput_msg TEXT, verror_msg TEXT)
RETURNS INTEGER
BEGIN
        DECLARE vid INTEGER;
        DECLARE vvstatus VARCHAR(10);
        DECLARE vdf_version INTEGER;
        DECLARE vdt_id INTEGER;

        SELECT dfv.version, dt.id INTO vdf_version, vdt_id
        FROM dataflow df, data_transformation dt, dataflow_version as dfv
        WHERE df.id = dt.df_id AND dfv.df_id = df.id AND df.tag = vdf_tag AND dt.tag = vdt_tag;

        IF((vdf_version IS NOT NULL) AND (vdt_id IS NOT NULL)) THEN
                SELECT t.id, t.status INTO vid, vvstatus
                FROM task t
                WHERE t.df_version = vdf_version AND t.dt_id = vdt_id AND t.identifier = videntifier;

                IF(vid IS NULL) THEN
                    #SELECT NEXT VALUE FOR "task_id_seq" into vid;
                    INSERT INTO task(identifier,df_version,dt_id,status,workspace,computing_resource,output_msg,error_msg) 
                    VALUES (videntifier,vdf_version,vdt_id,vstatus,vworkspace,vcomputing_resource,voutput_msg,verror_msg);
            ELSE
                UPDATE task
                SET status = vstatus, output_msg = voutput_msg, error_msg = verror_msg
                WHERE identifier = videntifier AND df_version = vdf_version AND dt_id = vdt_id;
                END IF;
    END IF;
        RETURN SELECT t.id FROM task t WHERE t.df_version = vdf_version AND t.dt_id = vdt_id AND t.identifier = videntifier;
END;

-- DROP FUNCTION insertFile;
CREATE FUNCTION insertFile (vtask_id INTEGER, vname VARCHAR(200), vpath VARCHAR(500))
RETURNS INTEGER
BEGIN
        DECLARE vid INTEGER;
    SELECT id INTO vid FROM file WHERE name=vname AND path=vpath;
    IF(vid IS NULL) THEN
        SELECT NEXT VALUE FOR "file_id_seq" into vid;
        INSERT INTO file(id,task_id,name,path) VALUES (vid,vtask_id,vname,vpath);
        END IF;
        RETURN vid;
END;

-- DROP FUNCTION insertPerformance;
CREATE FUNCTION insertPerformance (vtask_id INTEGER, vsubtask_id INTEGER, vmethod VARCHAR(30), vdescription VARCHAR(200), vstarttime VARCHAR(30), vendtime VARCHAR(30), vinvocation TEXT)
RETURNS INTEGER
BEGIN
        DECLARE vid INTEGER;
        IF(vsubtask_id IS NULL) THEN
                SELECT id INTO vid FROM performance WHERE method=vmethod and task_id=vtask_id;
        ELSE
                SELECT id INTO vid FROM performance WHERE method=vmethod and task_id=vtask_id and subtask_id=vsubtask_id;
        END IF;
    
    IF(vid IS NULL) THEN
        #SELECT NEXT VALUE FOR "performance_id_seq" into vid;
        INSERT INTO performance(task_id,subtask_id,method,description,starttime,endtime,invocation) VALUES (vtask_id,vsubtask_id,vmethod,vdescription,vstarttime,vendtime,vinvocation);
        ELSE
        UPDATE performance
        SET endtime = vendtime, invocation = vinvocation
        WHERE id = vid and endtime = 'null';
        END IF;
        
        IF(vsubtask_id IS NULL) THEN
                RETURN SELECT id FROM performance WHERE method=vmethod and task_id=vtask_id;
        ELSE
                RETURN SELECT id FROM performance WHERE method=vmethod and task_id=vtask_id and subtask_id=vsubtask_id;
        END IF;
END;


-- DROP FUNCTION insertExtractor;
CREATE FUNCTION insertExtractor (vtag VARCHAR(20), vds_id INTEGER, vcartridge VARCHAR(20), vextension VARCHAR(20))
RETURNS INTEGER
BEGIN
        DECLARE vid INTEGER;
    SELECT id INTO vid FROM extractor WHERE tag = vtag AND ds_id = vds_id AND cartridge = vcartridge AND extension = vextension;
    IF(vid IS NULL) THEN
        SELECT NEXT VALUE FOR "extractor_id_seq" into vid;
        INSERT INTO extractor(id,ds_id,tag,cartridge,extension) VALUES (vid,vds_id,vtag,vcartridge,vextension);
        END IF;
        RETURN vid;
END;

-- DROP FUNCTION insertExtractorCombination;
CREATE FUNCTION insertExtractorCombination (vouter_ext_id INTEGER, vinner_ext_id INTEGER, vds_id INTEGER, vkeys VARCHAR(100), vkey_types VARCHAR(100))
RETURNS INTEGER
BEGIN
        DECLARE vid INTEGER;
    SELECT id INTO vid FROM extractor_combination WHERE outer_ext_id = vouter_ext_id AND inner_ext_id = vinner_ext_id AND ds_id = vds_id;
    IF(vid IS NULL) THEN
        SELECT NEXT VALUE FOR "ecombination_id_seq" into vid;
        INSERT INTO extractor_combination(outer_ext_id,inner_ext_id,keys,key_types,ds_id) VALUES (vouter_ext_id,vinner_ext_id,vkeys,vkey_types,vds_id);
        END IF;
        RETURN vid;
END;

--views

create view ifilters(id, filters_task_id, timestamp, dataset_name) as
select ds.id, ds.filters_task_id, ds.timestamp, ds.dataset_name
 from ds_ifilters as ds
;
create view ofilters(id, filters_task_id, timestamp, filter_name) as
select ds.id, ds.filters_task_id, ds.timestamp, ds.filter_name
 from ds_ofilters as ds
;
create view ilayers(id, trainingmodel_task_id, timestamp, name, attribute_type, value) as
select ds.id, ds.trainingmodel_task_id, ds.timestamp, ds.name, ds.attribute_type, ds.value
 from ds_ilayers as ds
;
create view itrainingmodel(id, trainingmodel_task_id, timestamp, optimizer_name, learning_rate, decay, momentum, num_epochs, batch_size, num_layers) as
select ds.id, ds.trainingmodel_task_id, ds.timestamp, ds.optimizer_name, ds.learning_rate, ds.decay, ds.momentum, ds.num_epochs, ds.batch_size, ds.num_layers
 from ds_itrainingmodel as ds
;
create view otrainingmodel(id, trainingmodel_task_id, adaptation_task_id, testingmodel_task_id, timestamp, elapsed_time, loss, accuracy, val_loss, val_accuracy, epoch) as
select ds.id, ds.trainingmodel_task_id, ds.adaptation_task_id, ds.testingmodel_task_id, ds.timestamp, ds.elapsed_time, ds.loss, ds.accuracy, ds.val_loss, ds.val_accuracy, ds.epoch
 from ds_otrainingmodel as ds
;
create view oadaptation(id, adaptation_task_id, new_lrate, timestamp, epoch_id, adaptation_id) as
select ds.id, ds.adaptation_task_id, ds.new_lrate, ds.timestamp, ds.epoch_id, ds.adaptation_id
 from ds_oadaptation as ds
;
create view otestingmodel(id, testingmodel_task_id, timestamp, loss, accuracy) as
select ds.id, ds.testingmodel_task_id, ds.timestamp, ds.loss, ds.accuracy
 from ds_otestingmodel as ds
;
ALTER TABLE "ds_ifilters" ADD CONSTRAINT "ds_ifilters_filters_task_id_fkey" FOREIGN KEY ("filters_task_id") REFERENCES "public"."task" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "ds_ilayers" ADD CONSTRAINT "ds_ilayers_trainingmodel_task_id_fkey" FOREIGN KEY ("trainingmodel_task_id") REFERENCES "public"."task" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "ds_itrainingmodel" ADD CONSTRAINT "ds_itrainingmodel_trainingmodel_task_id_fkey" FOREIGN KEY ("trainingmodel_task_id") REFERENCES "public"."task" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "ds_oadaptation" ADD CONSTRAINT "ds_oadaptation_adaptation_task_id_fkey" FOREIGN KEY ("adaptation_task_id") REFERENCES "public"."task" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "ds_ofilters" ADD CONSTRAINT "ds_ofilters_filters_task_id_fkey" FOREIGN KEY ("filters_task_id") REFERENCES "public"."task" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "ds_otestingmodel" ADD CONSTRAINT "ds_otestingmodel_testingmodel_task_id_fkey" FOREIGN KEY ("testingmodel_task_id") REFERENCES "public"."task" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "ds_otrainingmodel" ADD CONSTRAINT "ds_otrainingmodel_trainingmodel_task_id_fkey" FOREIGN KEY ("trainingmodel_task_id") REFERENCES "public"."task" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "public"."attribute" ADD CONSTRAINT "attribute_ds_id_fkey" FOREIGN KEY ("ds_id") REFERENCES "public"."data_set" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "public"."attribute" ADD CONSTRAINT "attribute_extractor_id_fkey" FOREIGN KEY ("extractor_id") REFERENCES "public"."extractor" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "public"."data_dependency" ADD CONSTRAINT "data_dependency_ds_id_fkey" FOREIGN KEY ("ds_id") REFERENCES "public"."data_set" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "public"."data_dependency" ADD CONSTRAINT "data_dependency_next_dt_id_fkey" FOREIGN KEY ("next_dt_id") REFERENCES "public"."data_transformation" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "public"."data_dependency" ADD CONSTRAINT "data_dependency_previous_dt_id_fkey" FOREIGN KEY ("previous_dt_id") REFERENCES "public"."data_transformation" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "public"."data_set" ADD CONSTRAINT "data_set_df_id_fkey" FOREIGN KEY ("df_id") REFERENCES "public"."dataflow" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "public"."data_transformation" ADD CONSTRAINT "data_transformation_df_id_fkey" FOREIGN KEY ("df_id") REFERENCES "public"."dataflow" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "public"."dataflow_version" ADD CONSTRAINT "dataflow_version_df_id_fkey" FOREIGN KEY ("df_id") REFERENCES "public"."dataflow" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "public"."extractor" ADD CONSTRAINT "extractor_ds_id_fkey" FOREIGN KEY ("ds_id") REFERENCES "public"."data_set" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "public"."extractor_combination" ADD CONSTRAINT "extractor_combination_ds_id_fkey" FOREIGN KEY ("ds_id") REFERENCES "public"."data_set" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "public"."extractor_combination" ADD CONSTRAINT "extractor_combination_inner_ext_id_fkey" FOREIGN KEY ("inner_ext_id") REFERENCES "public"."extractor" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "public"."extractor_combination" ADD CONSTRAINT "extractor_combination_outer_ext_id_fkey" FOREIGN KEY ("outer_ext_id") REFERENCES "public"."extractor" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "public"."file" ADD CONSTRAINT "file_task_id_fkey" FOREIGN KEY ("task_id") REFERENCES "public"."task" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "public"."performance" ADD CONSTRAINT "performance_task_id_fkey" FOREIGN KEY ("task_id") REFERENCES "public"."task" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "public"."program" ADD CONSTRAINT "program_df_id_fkey" FOREIGN KEY ("df_id") REFERENCES "public"."dataflow" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "public"."task" ADD CONSTRAINT "task_df_version_fkey" FOREIGN KEY ("df_version") REFERENCES "public"."dataflow_version" ("version") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "public"."task" ADD CONSTRAINT "task_dt_id_fkey" FOREIGN KEY ("dt_id") REFERENCES "public"."data_transformation" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "public"."use_program" ADD CONSTRAINT "use_program_dt_id_fkey" FOREIGN KEY ("dt_id") REFERENCES "public"."data_transformation" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "public"."use_program" ADD CONSTRAINT "use_program_program_id_fkey" FOREIGN KEY ("program_id") REFERENCES "public"."program" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER SEQUENCE "ifilters_id_seq" RESTART WITH 9 NO CYCLE;
ALTER SEQUENCE "ilayers_id_seq" RESTART WITH 97 NO CYCLE;
ALTER SEQUENCE "itrainingmodel_id_seq" RESTART WITH 9 NO CYCLE;
ALTER SEQUENCE "oadaptation_id_seq" RESTART WITH 9 NO CYCLE;
ALTER SEQUENCE "ofilters_id_seq" RESTART WITH 9 NO CYCLE;
ALTER SEQUENCE "otestingmodel_id_seq" RESTART WITH 9 NO CYCLE;
ALTER SEQUENCE "otrainingmodel_id_seq" RESTART WITH 801 NO CYCLE;
COMMIT;


START TRANSACTION;
SET SCHEMA "public";
CREATE SEQUENCE "public"."att_id_seq" AS INTEGER;
CREATE SEQUENCE "public"."dd_id_seq" AS INTEGER;
CREATE SEQUENCE "public"."df_id_seq" AS INTEGER;
CREATE SEQUENCE "public"."ds_id_seq" AS INTEGER;
CREATE SEQUENCE "public"."dt_id_seq" AS INTEGER;
CREATE SEQUENCE "public"."ecombination_id_seq" AS INTEGER;
CREATE SEQUENCE "public"."extractor_id_seq" AS INTEGER;
CREATE SEQUENCE "public"."file_id_seq" AS INTEGER;
CREATE SEQUENCE "public"."performance_id_seq" AS INTEGER;
CREATE SEQUENCE "public"."program_id_seq" AS INTEGER;
CREATE SEQUENCE "public"."task_id_seq" AS INTEGER;
CREATE SEQUENCE "public"."version_id_seq" AS INTEGER;
CREATE TABLE "public"."dataflow" (
        "id"  INTEGER       NOT NULL DEFAULT next value for "public"."df_id_seq",
        "tag" VARCHAR(50)   NOT NULL,
        CONSTRAINT "dataflow_id_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "public"."dataflow_version" (
        "version" INTEGER       NOT NULL DEFAULT next value for "public"."version_id_seq",
        "df_id"   INTEGER       NOT NULL,
        CONSTRAINT "dataflow_version_version_pkey" PRIMARY KEY ("version")
);
COPY 1 RECORDS INTO "public"."dataflow_version" FROM stdin USING DELIMITERS '\t','\n','"';
1       1
CREATE TABLE "public"."data_transformation" (
        "id"    INTEGER       NOT NULL DEFAULT next value for "public"."dt_id_seq",
        "df_id" INTEGER       NOT NULL,
        "tag"   VARCHAR(50)   NOT NULL,
        CONSTRAINT "data_transformation_id_pkey" PRIMARY KEY ("id")
);
COPY 4 RECORDS INTO "public"."data_transformation" FROM stdin USING DELIMITERS '\t','\n','"';
1       1       "filters"
2       1       "trainingmodel"
3       1       "adaptation"
4       1       "testingmodel"
CREATE TABLE "public"."program" (
        "id"    INTEGER       NOT NULL DEFAULT next value for "public"."program_id_seq",
        "df_id" INTEGER       NOT NULL,
        "name"  VARCHAR(200)  NOT NULL,
        "path"  VARCHAR(500)  NOT NULL,
        CONSTRAINT "program_id_pkey" PRIMARY KEY ("id")
);
CREATE TABLE "public"."use_program" (
        "dt_id"      INTEGER       NOT NULL,
        "program_id" INTEGER       NOT NULL,
        CONSTRAINT "use_program_dt_id_program_id_pkey" PRIMARY KEY ("dt_id", "program_id")
);
CREATE TABLE "public"."data_set" (
        "id"    INTEGER       NOT NULL DEFAULT next value for "public"."ds_id_seq",
        "df_id" INTEGER       NOT NULL,
        "tag"   VARCHAR(50)   NOT NULL,
        CONSTRAINT "data_set_id_pkey" PRIMARY KEY ("id")
);
COPY 7 RECORDS INTO "public"."data_set" FROM stdin USING DELIMITERS '\t','\n','"';
1       1       "ifilters"
2       1       "ofilters"
3       1       "ilayers"
4       1       "itrainingmodel"
5       1       "otrainingmodel"
6       1       "oadaptation"
7       1       "otestingmodel"
CREATE TABLE "public"."data_dependency" (
        "id"             INTEGER       NOT NULL DEFAULT next value for "public"."dd_id_seq",
        "previous_dt_id" INTEGER,
        "next_dt_id"     INTEGER,
        "ds_id"          INTEGER       NOT NULL,
        CONSTRAINT "data_dependency_id_pkey" PRIMARY KEY ("id")
);
COPY 8 RECORDS INTO "public"."data_dependency" FROM stdin USING DELIMITERS '\t','\n','"';
1       NULL    1       1
2       NULL    1       2
3       NULL    2       3
4       NULL    2       4
5       2       3       5
6       3       NULL    6
7       2       4       5
8       4       NULL    7
CREATE TABLE "public"."extractor" (
        "id"        INTEGER       NOT NULL DEFAULT next value for "public"."extractor_id_seq",
        "ds_id"     INTEGER       NOT NULL,
        "tag"       VARCHAR(20)   NOT NULL,
        "cartridge" VARCHAR(20)   NOT NULL,
        "extension" VARCHAR(20)   NOT NULL,
        CONSTRAINT "extractor_id_pkey" PRIMARY KEY ("id")
);
CREATE TABLE "public"."extractor_combination" (
        "id"           INTEGER       NOT NULL DEFAULT next value for "public"."ecombination_id_seq",
        "ds_id"        INTEGER       NOT NULL,
        "outer_ext_id" INTEGER       NOT NULL,
        "inner_ext_id" INTEGER       NOT NULL,
        "keys"         VARCHAR(100)  NOT NULL,
        "key_types"    VARCHAR(100)  NOT NULL,
        CONSTRAINT "extractor_combination_id_pkey" PRIMARY KEY ("id")
);
CREATE TABLE "public"."attribute" (
        "id"           INTEGER       NOT NULL DEFAULT next value for "public"."att_id_seq",
        "ds_id"        INTEGER       NOT NULL,
        "extractor_id" INTEGER,
        "name"         VARCHAR(30),
        "type"         VARCHAR(15),
        CONSTRAINT "attribute_id_pkey" PRIMARY KEY ("id")
);
COPY 30 RECORDS INTO "public"."attribute" FROM stdin USING DELIMITERS '\t','\n','"';
1       1       NULL    "timestamp"     "TEXT"
2       1       NULL    "dataset_name"  "TEXT"
3       2       NULL    "timestamp"     "TEXT"
4       2       NULL    "filter_name"   "TEXT"
5       3       NULL    "timestamp"     "TEXT"
6       3       NULL    "name"  "TEXT"
7       3       NULL    "attribute_type"        "TEXT"
8       3       NULL    "value" "TEXT"
9       4       NULL    "timestamp"     "TEXT"
10      4       NULL    "optimizer_name"        "TEXT"
11      4       NULL    "learning_rate" "NUMERIC"
12      4       NULL    "decay" "NUMERIC"
13      4       NULL    "momentum"      "NUMERIC"
14      4       NULL    "num_epochs"    "NUMERIC"
15      4       NULL    "batch_size"    "NUMERIC"
16      4       NULL    "num_layers"    "NUMERIC"
17      5       NULL    "timestamp"     "TEXT"
18      5       NULL    "elapsed_time"  "TEXT"
19      5       NULL    "loss"  "NUMERIC"
20      5       NULL    "accuracy"      "NUMERIC"
21      5       NULL    "val_loss"      "NUMERIC"
22      5       NULL    "val_accuracy"  "NUMERIC"
23      5       NULL    "epoch" "NUMERIC"
24      6       NULL    "new_lrate"     "NUMERIC"
25      6       NULL    "timestamp"     "TEXT"
26      6       NULL    "epoch_id"      "NUMERIC"
27      6       NULL    "adaptation_id" "NUMERIC"
28      7       NULL    "timestamp"     "TEXT"
29      7       NULL    "loss"  "NUMERIC"
30      7       NULL    "accuracy"      "NUMERIC"
CREATE TABLE "public"."task" (
        "id"                 INTEGER       NOT NULL DEFAULT next value for "public"."task_id_seq",
        "identifier"         INTEGER       NOT NULL,
        "df_version"         INTEGER       NOT NULL,
        "dt_id"              INTEGER       NOT NULL,
        "status"             VARCHAR(10),
        "workspace"          VARCHAR(500),
        "computing_resource" VARCHAR(100),
        "output_msg"         CHARACTER LARGE OBJECT,
        "error_msg"          CHARACTER LARGE OBJECT,
        CONSTRAINT "task_id_pkey" PRIMARY KEY ("id")
);
COPY 4 RECORDS INTO "public"."task" FROM stdin USING DELIMITERS '\t','\n','"';
1       1       1       1       "FINISHED"      "null"  "null"  "null"  "null"
2       2       1       2       "FINISHED"      "null"  "null"  "null"  "null"
3       4       1       3       "FINISHED"      "null"  "null"  "null"  "null"
4       4       1       4       "FINISHED"      "null"  "null"  "null"  "null"
CREATE TABLE "public"."file" (
        "id"      INTEGER       NOT NULL DEFAULT next value for "public"."file_id_seq",
        "task_id" INTEGER       NOT NULL,
        "name"    VARCHAR(200)  NOT NULL,
        "path"    VARCHAR(500)  NOT NULL,
        CONSTRAINT "file_id_pkey" PRIMARY KEY ("id")
);
CREATE TABLE "public"."performance" (
        "id"          INTEGER       NOT NULL DEFAULT next value for "public"."performance_id_seq",
        "task_id"     INTEGER       NOT NULL,
        "subtask_id"  INTEGER,
        "method"      VARCHAR(30)   NOT NULL,
        "description" VARCHAR(200),
        "starttime"   VARCHAR(30),
        "endtime"     VARCHAR(30),
        "invocation"  CHARACTER LARGE OBJECT,
        CONSTRAINT "performance_id_pkey" PRIMARY KEY ("id")
);
COPY 4 RECORDS INTO "public"."performance" FROM stdin USING DELIMITERS '\t','\n','"';
1       1       NULL    "null"  "null"  "2021-03-24 21:46:14"   "2021-03-24 21:46:14"   "null"
2       3       NULL    "null"  "null"  "2021-03-24 21:53:07"   "2021-03-24 21:53:07"   "null"
3       2       NULL    "null"  "null"  "2021-03-24 21:46:19"   "2021-03-24 22:21:45"   "null"
4       4       NULL    "null"  "null"  "2021-03-24 22:21:46"   "2021-03-24 22:21:46"   "null"
create function insertdataflow (v_tag varchar(50))
returns integer
begin
 declare v_df_id integer;
 select df.id into v_df_id from dataflow df where df.tag=v_tag;
 if(v_df_id is null) then
 #SELECT NEXT VALUE FOR "df_id_seq" into v_df_id;
 insert into dataflow(tag) values (v_tag);
 end if;
 return select df.id from dataflow df where df.tag=v_tag;
end;
create function insertdataflowversion (vdf_id integer)
returns integer
begin
 declare version_id integer;
 #SELECT NEXT VALUE FOR "version_id_seq" into version_id;
 insert into dataflow_version(df_id) values (vdf_id);
 return select dfv.version from dataflow_version dfv where dfv.df_id=vdf_id and dfv.version=get_value_for('public', 'version_id_seq');
end;
create function insertdatatransformation (vdf_id integer, vtag varchar(50))
returns integer
begin
 declare vdt_id integer;
 select id into vdt_id from data_transformation where df_id = vdf_id and tag = vtag;
 if(vdt_id is null) then
 #SELECT NEXT VALUE FOR "dt_id_seq" into vdt_id;
 insert into data_transformation(df_id,tag) values (vdf_id,vtag);
 end if;
 return select id from data_transformation where df_id = vdf_id and tag = vtag;
end;
create function insertprogram (vdf_id integer, vdt_id integer, vname varchar(200), vpath varchar(500))
returns integer
begin
 declare vprogram_id integer;
 select id into vprogram_id from program p where df_id = vdf_id and name = vname and path = vpath;
 if(vprogram_id is null) then
 select next value for "program_id_seq" into vprogram_id;
 insert into program(id,df_id,name,path) values (vprogram_id,vdf_id,vname,vpath);
 end if;
 insert into use_program(dt_id,program_id) values (vdt_id,vprogram_id);
 return vprogram_id;
end;
create function insertdataset (vdf_id integer, vdt_id integer, vdep_dt_id integer, vtag varchar(500), vtype varchar(10))
returns integer
begin
 declare vds_id integer;
 select id into vds_id from data_set ds where df_id = vdf_id and tag = vtag;
 if(vds_id is null) then
 #SELECT NEXT VALUE FOR "ds_id_seq" into vds_id;
 insert into data_set(df_id,tag) values (vdf_id,vtag);
 select id into vds_id from data_set ds where df_id = vdf_id and tag = vtag;
 end if;
 if(vdep_dt_id is not null) then
 declare vdd_id integer;
 select ds_id into vdd_id from data_dependency
 where previous_dt_id = vdep_dt_id and next_dt_id = vdt_id and ds_id = vds_id;
 declare vid integer;
 select id into vid from data_dependency where previous_dt_id = vdep_dt_id and next_dt_id is null;
 if(vid is null) then
 if(vdd_id is null) then
 declare vdd_id integer;
 #SELECT NEXT VALUE FOR "dd_id_seq" into vdd_id;
 insert into data_dependency(previous_dt_id,next_dt_id,ds_id) values (vdep_dt_id,vdt_id,vds_id);
 end if;
 else
 update data_dependency set next_dt_id = vdt_id where id = vid;
 end if;
 else
 declare vdd_id integer;
 #SELECT NEXT VALUE FOR "dd_id_seq" into vdd_id;
 if(vtype like 'INPUT') then
 insert into data_dependency(previous_dt_id,next_dt_id,ds_id) values (null,vdt_id,vds_id);
 else
 insert into data_dependency(previous_dt_id,next_dt_id,ds_id) values (vdt_id,null,vds_id);
 end if;
 end if;
 return vds_id;
end;
create function insertattribute (dds_id integer, vextractor_id integer, vname varchar(30), vtype varchar(15))
returns integer
begin
 declare vid integer;
 select id into vid from attribute where ds_id=dds_id and name=vname;
 if(vid is null) then
 #SELECT NEXT VALUE FOR "att_id_seq" into vid;
 insert into attribute(ds_id,extractor_id,name,type) values (dds_id,vextractor_id,vname,vtype);
 end if;
 return select id from attribute where ds_id=dds_id and name=vname;
end;
create function inserttask (videntifier integer, vdf_tag varchar(50), vdt_tag varchar(50), vstatus varchar(10), vworkspace varchar(500),
 vcomputing_resource varchar(100), voutput_msg text, verror_msg text)
returns integer
begin
 declare vid integer;
 declare vvstatus varchar(10);
 declare vdf_version integer;
 declare vdt_id integer;
 select dfv.version, dt.id into vdf_version, vdt_id
 from dataflow df, data_transformation dt, dataflow_version as dfv
 where df.id = dt.df_id and dfv.df_id = df.id and df.tag = vdf_tag and dt.tag = vdt_tag;
 if((vdf_version is not null) and (vdt_id is not null)) then
 select t.id, t.status into vid, vvstatus
 from task t
 where t.df_version = vdf_version and t.dt_id = vdt_id and t.identifier = videntifier;
 if(vid is null) then
 #SELECT NEXT VALUE FOR "task_id_seq" into vid;
 insert into task(identifier,df_version,dt_id,status,workspace,computing_resource,output_msg,error_msg)
 values (videntifier,vdf_version,vdt_id,vstatus,vworkspace,vcomputing_resource,voutput_msg,verror_msg);
 else
 update task
 set status = vstatus, output_msg = voutput_msg, error_msg = verror_msg
 where identifier = videntifier and df_version = vdf_version and dt_id = vdt_id;
 end if;
 end if;
 return select t.id from task t where t.df_version = vdf_version and t.dt_id = vdt_id and t.identifier = videntifier;
end;
create function insertfile (vtask_id integer, vname varchar(200), vpath varchar(500))
returns integer
begin
 declare vid integer;
 select id into vid from file where name=vname and path=vpath;
 if(vid is null) then
 select next value for "file_id_seq" into vid;
 insert into file(id,task_id,name,path) values (vid,vtask_id,vname,vpath);
 end if;
 return vid;
end;
create function insertperformance (vtask_id integer, vsubtask_id integer, vmethod varchar(30), vdescription varchar(200), vstarttime varchar(30), vendtime varchar(30), vinvocation text)
returns integer
begin
 declare vid integer;
 if(vsubtask_id is null) then
 select id into vid from performance where method=vmethod and task_id=vtask_id;
 else
 select id into vid from performance where method=vmethod and task_id=vtask_id and subtask_id=vsubtask_id;
 end if;

 if(vid is null) then
 #SELECT NEXT VALUE FOR "performance_id_seq" into vid;
 insert into performance(task_id,subtask_id,method,description,starttime,endtime,invocation) values (vtask_id,vsubtask_id,vmethod,vdescription,vstarttime,vendtime,vinvocation);
 else
 update performance
 set endtime = vendtime, invocation = vinvocation
 where id = vid and endtime = 'null';
 end if;

 if(vsubtask_id is null) then
 return select id from performance where method=vmethod and task_id=vtask_id;
 else
 return select id from performance where method=vmethod and task_id=vtask_id and subtask_id=vsubtask_id;
 end if;
end;
create function insertextractor (vtag varchar(20), vds_id integer, vcartridge varchar(20), vextension varchar(20))
returns integer
begin
 declare vid integer;
 select id into vid from extractor where tag = vtag and ds_id = vds_id and cartridge = vcartridge and extension = vextension;
 if(vid is null) then
 select next value for "extractor_id_seq" into vid;
 insert into extractor(id,ds_id,tag,cartridge,extension) values (vid,vds_id,vtag,vcartridge,vextension);
 end if;
 return vid;
end;
create function insertextractorcombination (vouter_ext_id integer, vinner_ext_id integer, vds_id integer, vkeys varchar(100), vkey_types varchar(100))
returns integer
begin
 declare vid integer;
 select id into vid from extractor_combination where outer_ext_id = vouter_ext_id and inner_ext_id = vinner_ext_id and ds_id = vds_id;
 if(vid is null) then
 select next value for "ecombination_id_seq" into vid;
 insert into extractor_combination(outer_ext_id,inner_ext_id,keys,key_types,ds_id) values (vouter_ext_id,vinner_ext_id,vkeys,vkey_types,vds_id);
 end if;
 return vid;
end;
ALTER TABLE "ds_ifilters" ADD CONSTRAINT "ds_ifilters_filters_task_id_fkey" FOREIGN KEY ("filters_task_id") REFERENCES "public"."task" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "ds_ilayers" ADD CONSTRAINT "ds_ilayers_trainingmodel_task_id_fkey" FOREIGN KEY ("trainingmodel_task_id") REFERENCES "public"."task" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "ds_itrainingmodel" ADD CONSTRAINT "ds_itrainingmodel_trainingmodel_task_id_fkey" FOREIGN KEY ("trainingmodel_task_id") REFERENCES "public"."task" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "ds_oadaptation" ADD CONSTRAINT "ds_oadaptation_adaptation_task_id_fkey" FOREIGN KEY ("adaptation_task_id") REFERENCES "public"."task" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "ds_ofilters" ADD CONSTRAINT "ds_ofilters_filters_task_id_fkey" FOREIGN KEY ("filters_task_id") REFERENCES "public"."task" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "ds_otestingmodel" ADD CONSTRAINT "ds_otestingmodel_testingmodel_task_id_fkey" FOREIGN KEY ("testingmodel_task_id") REFERENCES "public"."task" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "ds_otrainingmodel" ADD CONSTRAINT "ds_otrainingmodel_trainingmodel_task_id_fkey" FOREIGN KEY ("trainingmodel_task_id") REFERENCES "public"."task" ("id") ON DELETE CASCADE ON UPDATE CASCADE;

COMMIT;
