

// Place different queries for BoaFilter to run here
public enum queries {
	
	// Top ten languages query
	QUERY_TopTenLang("p: Project = input;\n" +
			  "counts: output top(10) of string weight int;\n" +
			  "foreach (i: int; def(p.programming_languages[i]))\n" +
			  "	counts << p.programming_languages[i] weight 1;");
	
	private final String text;
	
	private queries(final String text){
		this.text = text;
		
	}
	
	@Override
	public String toString(){
		return text;
		
	}
	
	
	
}
