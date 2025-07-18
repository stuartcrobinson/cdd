# CDD: Covenant-Driven Development 🤝

the point is to be a framework for LLMs to effectively do software developmenet.  formalizing dependencies for components including inthe documentation.  for auto context assembly

but honeslty lately i'm feeling like the covenants are overkill.  the extra step is just a ton of work.  we should just write the tests.  but maybe the design should be to always use dynamic tests?  and externalize the test cases into .json or .md files. thats what we did for sham-parserjs === nesl-js.  seems good, sensible, clear, explicit.  easy to read.  

yeah i feel p strongly about that.  each unit test should be a single tiny code file that just pulls in all the test cases from an exteranl test cases file or dir. horrible when input/outputs are embedded in the test code.  "specs" are horrible ... given/ expect / blah blah blah... just list out all expectiations in the structured format that the test will directly read and test

lets call this ... dynamic tests ... formalized dependency management among documentation ... documentation driven development ... test driven developement

## how i use

for now, its just about getting the cdd_ref document into other projects to feed the LLM during dev. 


post install script in package.json in my node project to download CDD_ref.md into my project root for easy adding to LLM context

```json
{
  "name": "your-project",
  "version": "1.0.0",
  "scripts": {
    "postinstall": "npm run download-CDD_ref",
    "download-CDD_ref": "curl -L -o CDD_ref.md https://github.com/stuartcrobinson/cdd/blob/main/CDD_ref.md"
  }
}
```