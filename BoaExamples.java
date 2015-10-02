/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package boaexamples;

import edu.iastate.cs.boa.*;
import java.util.logging.Level;
import java.util.logging.Logger;


/**
 *
 * @author Charles
 */
public class BoaExamples {

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        
        try {
            foo();
        } catch (Exception ex) {
            //do nothing
            System.out.println("Shit happened!!");
        }
        
        
    }
    
    
    public static void foo() throws Exception{
        BoaClient client = new BoaClient();
        client.login("cgathuru", "msrdataset");
        int jobs = client.getJobCount();
        System.out.println("Have run " + jobs +" jobs");
        String query = "p: Project = input;\n" +
"counts: output top(10) of string weight int;\n" +
"\n" +
"foreach (i: int; def(p.programming_languages[i]))\n" +
"	counts << p.programming_languages[i] weight 1;";
        JobHandle handle = client.query(query);
        System.out.println("WE have queiried");
        waitAndGetOutput(handle);
    }
    
    public static String waitAndGetOutput(JobHandle outputHandle) throws Exception{
        String output = "";
        while(true){
            outputHandle.refresh();
            //System.out.println(outputHandle.getExecutionStatus());
            if(outputHandle.getExecutionStatus().equals(ExecutionStatus.FINISHED)){
                break;
            }
            
        }
        output = outputHandle.getOutput();
        System.out.println("The response has " + output);
        return null;
    }
}
