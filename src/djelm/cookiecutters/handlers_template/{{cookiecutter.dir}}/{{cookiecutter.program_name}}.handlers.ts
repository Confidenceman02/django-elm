interface ElmApp {
  ports: {
    [portName: string]: {
      subscribe?: (callback: (data: any) => void) => void;
      send?: (data: any) => void;
    };
  };
  die?: () => null;
}

export function handleApp(app: ElmApp): void {
  console.warn(
    "'handleApp' Not implemented for '{{cookiecutter.program_name}}.elm'",
  );
}
