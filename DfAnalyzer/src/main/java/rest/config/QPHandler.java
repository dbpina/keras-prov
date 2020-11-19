package rest.config;

import com.google.common.base.Stopwatch;
import java.io.IOException;
import java.sql.SQLException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import qp.dataflow.Dataflow;
import qp.query.MonetDbSqlQuery;
import qp.query.QueryProcessor;
import qp.query.QuerySpecification;

/**
 *
 * @author vitor
 */
@Service
public class QPHandler {
    
    @Autowired
    private DbConnection db;

    public String runQuery(String dataflowTag, Integer dataflowID, String message) throws IOException, SQLException {
        //load dataflow from provenance database
        QuerySpecification spec = new QuerySpecification(dataflowTag, dataflowID, message);
        Dataflow dataflow = db.loadDataflow(spec);
        //generate query
        QueryProcessor qp = new QueryProcessor(db, dataflow);
        Stopwatch stopwatch1 = Stopwatch.createStarted();    
        MonetDbSqlQuery query = qp.runSqlQuery(spec);
        //answer
        StringBuilder answer = new StringBuilder();
        answer.append(query.toString());
        answer.append("\n================================================");        
        answer.append("\nQuery elapsed time (generation + execution): " + stopwatch1);
        answer.append("\n================================================");
        String currentPath = System.getProperty("user.dir");
        answer.append("\nCurrentPath:" + currentPath);
        return answer.toString();
    }
    
    
}
