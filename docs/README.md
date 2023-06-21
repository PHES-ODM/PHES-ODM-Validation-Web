# **docs** folder

All the documentation for the tool is contained in this folder. The high level
folder structure is described below:

* **tool-specifications/**: Contains the high level specifications for the tool
* **ui-specifications/**: Contains the UI specifications for the tool

## UI Specifications

The UI specifications document is contained in the [ui-specifications.qmd](./ui-specifications/ui-specifications.qmd)
file.

The wireframes are all written using [PlantUML](https://plantuml.com/) and are
contained in the [wireframe](./ui-specifications/wireframes) folder. The folder
structure is described below:

* [screens](./ui-specifications/wireframes/screens): Contains the wireframes for
  the screens
* [user-flows](./ui-specifications/wireframes/user-flows): Contains the flow 
  diagrams.

### Building the UI Specifications

Requirements:

* [PlantUML and its dependencies](https://plantuml.com/starting)
* [Quarto](https://quarto.org/docs/get-started/)

Build Steps:

1. Build the wireframe documents by running the command below, 

   `java -jar E:/plantuml.jar -o ../../../../dist "./docs/ui-specifications/wireframe*/**.puml"` 

   This will convert all the wireframe documents into images and put them in the
   dist folder in the root of the project.
    
   PlantUML will report the errors below:

   ```
   Error line 2 in file: .\docs\ui-specifications\wireframes\screens\screens.puml
   Error line 2 in file: .\docs\ui-specifications\wireframes\user-flows\user-flows.puml
   Some diagram description contains errors
   ```

   which is expected. Those files don't contain diagrams, only procedures, which
   makes the tool complain.
2. Build the quarto document by running the command below,

   `quarto render ./docs/ui-specifications/ui-specifications.qmd`

   This will convert the quarto file into an HTML file which will be available
   at `dist/ui-specifications/ui-specifications.html` at the project root.

### Idiosyncrasies

* All the wireframes should be located at the same level relative to the 
  wireframes document. PlantUML won't output the files in the same directory if
  the files are at different levels. More information [here](https://plantuml.com/command-line#6d10d2b95e98aa85)
* PlantUML does not allow the text returned from a procedure directly inside a 
  UML diagram. It can only be used inside another procedure. For example,

  ```
  @startuml

  !procedure $home_screen()
    salt
    {
        Home Screen
    }
  !endprocedure

  !procedure $user_flow($screen)
    (*) -> [user opens the home screen]"
    {{
        $home_screen()
    }}
    " as home_screen
  !endprocedure

  $user_flow($home_screen())

  @enduml
  ```

  The above will return an error. 

  To go around this limitation we use [`%invoke_procedure`](https://plantuml.com/preprocessing#5a1670d800446678)
  and if the procedure takes an argument we create a wrapped procedure and pass
  it in to be invoked
