/*
  Do not manually edit this file, it was auto-generated by djelm
  https://github.com/Confidenceman02/djelm
*/
import defo from "@icelab/defo";

const views = {
  djelm{{cookiecutter.program_name}}: async (el: HTMLElement, data: any) => {
    console.log("Hello from defo!")
    //@ts-ignore
    const { Elm } = await import("../src/{{cookiecutter.program_name}}.elm")

    const app = Elm.{{cookiecutter.program_name}}.init({
      node: el,
      flags: data,
    });

    return {
      // Called whenever the value of the `defo` attribute changes
      update: (newData, oldData) => {
        console.log("Updated")
      },
      // Caled when the element (or its defo attribute) is removed from the DOM
      destroy: () => {
        console.log("destroyed")
      }
    };
  }
}

defo({ views, prefix: "{{cookiecutter.scope}}" })