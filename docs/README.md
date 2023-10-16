# **docs** folder

All the documentation for the tool is contained in this folder. The high level
folder structure is described below:

* **tool-spec/**: Contains the high level specifications for the tool
* **ui-spec/**: Contains the UI specifications for the tool
* **tech-spec/**: Contains the low level technical specifications for the tool

## UI Specifications

The UI specifications document is contained in the [ui-spec.qmd](./ui-spec/ui-spec.qmd)
file.

The wireframes are all written using [PlantUML](https://plantuml.com/) and are
contained in the [wireframe](./ui-spec/wireframes) folder. The folder
structure is described below:

* [pages](./ui-spec/wireframes/pages): Contains the wireframes for
  the pages
* [dialogs](./ui-spec/wireframes/dialogs): Contains the wireframes for
  the dialogs
* [user-flows](./ui-spec/wireframes/user-flows): Contains the flow
  diagrams.

### Building the UI Specifications

Requirements:

* [PlantUML and its dependencies](https://plantuml.com/starting)
* [Quarto](https://quarto.org/docs/get-started/)

Build Steps:

1. Build the wireframe documents by running the command below,

   ```
   java \
       -jar <plantuml-dir>/plantuml.jar \
       -o ../../../../dist \
       "./docs/ui-spec/wireframes/**/*.puml"
   ```

   This will convert all the wireframe documents into images and put them in the
   dist folder in the root of the project.

   PlantUML will report the errors below:

   ```
   Error line 2 in file: ./docs/ui-spec/wireframes/components/components.puml
   Error line 2 in file: ./docs/ui-spec/wireframes/screens.puml
   Error line 2 in file: ./docs/ui-spec/wireframes/user-flows/user-flows.puml
   Some diagram description contains errors
   ```

   which is expected. Those files don't contain diagrams, only procedures, which
   makes the tool complain.
2. Once the images have been generated, Quarto is used to build the
   documentation website. To build and view the entire website use the command
   below,

   ```
   quarto preview ./docs
   ```

   Once the build is done it will open a browser tab with the website loaded.
   Subsequent changes to the documentation will rebuild and reload the website.

   To build a specific documentation page the following command can be used,

   `quarto render ./docs/ui-spec/ui-spec.qmd`

   This will convert the quarto file into an HTML file which will be available
   at `dist/ui-spec/ui-spec.html` at the project root.

   This has the advantage of being faster.

### Idiosyncrasies

* All the wireframes should be located at the same level relative to the
  wireframes document. PlantUML won't output the files in the same directory if
  the files are at different levels. More information [here](https://plantuml.com/command-line#6d10d2b95e98aa85)
* PlantUML does not allow the text returned from a procedure directly inside a
  UML diagram. It can only be used inside another procedure. For example,

  ```
  @startuml

  !procedure $home_page()
    salt
    {
        Home Page
    }
  !endprocedure

  !procedure $user_flow($page)
    (*) -> [user opens the home page]"
    {{
        $home_page()
    }}
    " as home_page
  !endprocedure

  $user_flow($home_page())

  @enduml
  ```

  The above will return an error.

  To go around this limitation we use [`%invoke_procedure`](https://plantuml.com/preprocessing#5a1670d800446678)
  and if the procedure takes an argument we create a wrapped procedure and pass
  it in to be invoked
* In the **Validation Summary** and **View Dataset** pages, there is a large
  space between the sidebar and the main content. This is not intended but
  we're unsure how to fix it.
