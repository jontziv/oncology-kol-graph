// Allow CSS module imports
declare module "*.css" {
  const content: Record<string, string>;
  export default content;
}

// react-simple-maps v3 doesn't ship TS types — declare as module
declare module "react-simple-maps";
