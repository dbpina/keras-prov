package di.object.task;

import di.object.dataflow.Set;
import di.enumeration.dataflow.DataflowType;
import java.util.ArrayList;
import java.util.HashMap;
import di.dataflow.object.DataflowObject;

/**
 *
 * @author vitor
 */
public class Task extends DataflowObject {

    public String transformationTag = "";
    public Integer ID = null;
    public Integer subID = null;
    public String resource = "";
    public String workspace = "";
    public String status = "";
    public String output = "";
    public String error = "";
    public Integer first = null;
    public String execTag = "";
    public ArrayList<dfFile> files = new ArrayList<>();
    public ArrayList<Element> elements = new ArrayList<>();
    public ArrayList<String> dependencyTags = new ArrayList<>();
    public ArrayList<String[]> dependencyIDs = new ArrayList<>();
    public ArrayList<HashMap<String, Integer>> dependencyTaskIDs = new ArrayList<>();
    public ArrayList<Performance> performances = new ArrayList<Performance>();   

    protected Task(DataflowType type) {
        super(type);
    }

    public Task() {
        this(DataflowType.TASK);
    }
    
    public void updateFiles(Set set) {
        for (Element e : elements) {
            if (e.setTag.equals(set.tag) && !set.extractors.isEmpty()) {
                files.addAll(e.getFilesFromExtractors(set.extractors.size()));
            }
        }
    }

}
