import java.util.Scanner;

import edu.iastate.cs.boa.BoaClient;
import edu.iastate.cs.boa.BoaException;
import edu.iastate.cs.boa.ExecutionStatus;
import edu.iastate.cs.boa.InputHandle;
import edu.iastate.cs.boa.JobHandle;
import edu.iastate.cs.boa.LoginException;
import edu.iastate.cs.boa.NotLoggedInException;

public class BoaFilter {

	private static BoaClient client;
	
	// General method for initiating logons and queries
	// Library of queries can be found within the 'queries' class
	public static void main(String[] args) throws BoaException {
		
		// Variables and objects
		int z,i = 0;
		boolean retry = true;
		String[] credentials = new String[2]; 		// Create string[] of username and password
		InputHandle[] availDataSets = new InputHandle[15];	// Data Sets available to user
		Scanner userInput = new Scanner(System.in); // Scanner for UI
		client = new BoaClient(); 					// Create an instance of the Boa client
		InputHandle dataSet = null; 		// Allows for user to select data set to read from
		
		
		// *********** Begin User Interface ***********
		
		// Have user enter credentials
		System.out.print("\nUsername: ");
		credentials[0] = userInput.next();
		System.out.print("Password: ");
		credentials[1] = userInput.next();
		
		System.out.println("\nAttempting login to Boa servers...");
		
		try{
			// Logon to client
			client.login(credentials[0], credentials[1]);
			
			System.out.println("Success!\n");
			
			// List available data sets
			System.out.println("Available data sets: ");
			for (final InputHandle d : client.getDatasets()){
				System.out.println((i+1) + ". " + d);
				availDataSets[i] = d;
				i++;
			}
			
			while (retry){
				// Have user choose data set
					System.out.print("\nEnter the integer of the desired data set: ");
					z = userInput.nextInt();
				
					dataSet = availDataSets[i-1];
					if (dataSet == null){
						System.out.println("Could not find specified data set, try again");
					
					}
					else {
						System.out.println("Data set " + availDataSets[z-1] + " selected!");
						retry = false;
						
					}
				}
		}
		catch (LoginException e){
			e.printStackTrace();
			System.out.println("Login failed");
			System.exit(0);
		}	
		catch (BoaException e){
			e.printStackTrace();
			System.out.println("Error reading data sets from server");
			System.exit(0);
		}
		
		// ************ End User Interface ************
		
		// Queries to be run
		String query1 = new String(queries.QUERY_TopTenLang.toString());
		
		// Run Boa query one
		z = runQuery(query1, dataSet);
		
		// Standard error report - should be inserted every time runQuery is called
		if (z != 0){
			System.out.println("Query failed");
			if (z == 1){
				System.out.println("Exception error in runQuery method");
			}
			else if (z == 2){
				System.out.println("Exception error in waitAndGetOutput method");
			}
			System.exit(0);
		}
		
	}
	
	
	// Method for running Boa queries
	public static int runQuery(String query, InputHandle dataSet) throws BoaException{
		
		String status = new String();
		
		System.out.println("\nAttempting to run new query...");
		
		try{
			// Run entered query
			JobHandle out = client.query(query, dataSet);
			
			// Wait for query output
			status = waitAndGetOutput(out);
			if (status == "fail"){
				return 2;
			}
			
		}
		catch(BoaException e) {
			e.printStackTrace();
			return 1;
		}
				
		return 0;
		
	}
	
	// Method for waiting on Boa queries and obtaining their results
	public static String waitAndGetOutput(JobHandle outputHandle){
		
		String output = new String();
		
		System.out.println("Waiting on query output...");
		
		try {
			// Refresh status of output, once completed exit
			// Only print the status once to avoid clutter in terminal
			while(true){
				outputHandle.refresh();
				
				if (outputHandle.getExecutionStatus().equals(ExecutionStatus.FINISHED)){
					System.out.println("Finished!\n");
					output = outputHandle.getOutput();
					break;
					
				}
				else if (output != "Waiting..." && outputHandle.getExecutionStatus().equals(ExecutionStatus.WAITING)) {
					output = "Waiting...";
					
				}
				else if (output != "Running..." && outputHandle.getExecutionStatus().equals(ExecutionStatus.RUNNING)){
					output = "Running...";
					System.out.println(output);
					
				}
			}
		
				System.out.println("The response to the query is: \n" + output);
				System.out.println();
		}
		catch (NotLoggedInException e){
			e.printStackTrace();
			return "fail";
		}
		catch (BoaException e){
			e.printStackTrace();
			return "fail";
		}
		
		// Temporary	
		return "";
		
	}
}


