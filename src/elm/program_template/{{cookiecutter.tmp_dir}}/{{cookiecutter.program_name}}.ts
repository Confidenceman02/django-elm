//@ts-ignore
import { Elm } from "../src/{{cookiecutter.program_name}}.elm";
import defo from "@icelab/defo";

const views = {
  djelm{{cookiecutter.program_name}}: (el, data) => {
    console.log("Hello from defo!")

    return {
      // Called whenever the value of the `defo` attribute changes
      update: (newData, oldData) => {
      },
      // Caled when the element (or its defo attribute) is removed from the DOM
      destroy: () => {
      }
    };
  }
}

defo({ views, scope: "{{cookiecutter.scope}}" })
