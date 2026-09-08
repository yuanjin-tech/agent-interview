import { defineConfig } from "astro/config";

const repository = process.env.GITHUB_REPOSITORY?.split("/")[1];
const isUserSite = repository?.endsWith(".github.io");
const base = process.env.GITHUB_ACTIONS && repository && !isUserSite ? `/${repository}` : "/";
const owner = process.env.GITHUB_REPOSITORY_OWNER;
const site = owner ? `https://${owner}.github.io` : undefined;

export default defineConfig({
  base,
  site,
  output: "static",
  trailingSlash: "always",
  build: {
    format: "directory"
  }
});
