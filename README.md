# PHES-ODM-Validation-web

## Wireframes

Run the following command to build the wireframe images

```
java -jar E:/plantuml.jar -o ../../../dist "./docs/wireframe*/**.puml"
```

The images should be in the **dist** folder in the root of the project.

The following message will be shown by the tool which cane be ignored,

```
Error line 2 in file: .\docs\wireframe\screens.puml
Some diagram description contains errors
```

### Idiosyncrancies

* All the wireframes should be in the `user-flows` directory due to the "weird"
  way that PlantUML handles relative paths in the output. If all the files are
  not in the same directory then we can't output all the images in to the same
  folder. More information [here](https://plantuml.com/command-line#6d10d2b95e98aa85)
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

  the above will return an error. 

  To go around this limitation we use [`%invoke_procedure`](https://plantuml.com/preprocessing#5a1670d800446678)
  and if the procedure takes an argument we create a wrapped procedure and pass
  in to be invoked
