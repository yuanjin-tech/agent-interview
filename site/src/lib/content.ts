import fs from "node:fs";
import path from "node:path";

import { load as loadYaml } from "js-yaml";
import MarkdownIt from "markdown-it";

export type Difficulty = "easy" | "medium" | "hard";

interface CatalogEntry {
  id: string;
  title: string;
  difficulty: Difficulty;
}

type Catalog = Record<string, CatalogEntry[]>;

export interface Question extends CatalogEntry {
  categories: string[];
  index: number;
  answerHtml: string;
  pointsHtml: string;
  referencesHtml: string;
  description: string;
  searchText: string;
}

const workingDirectory = process.cwd();
const projectRoot = fs.existsSync(path.join(workingDirectory, "catalog.yaml"))
  ? workingDirectory
  : path.resolve(workingDirectory, "..");
const markdown = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: false
});

markdown.renderer.rules.link_open = (tokens, index, options, env, self) => {
  const token = tokens[index];
  const href = token.attrGet("href") ?? "";
  if (/^https?:\/\//.test(href)) {
    token.attrSet("target", "_blank");
    token.attrSet("rel", "noopener noreferrer");
  }
  return self.renderToken(tokens, index, options);
};

function splitSections(source: string): Record<string, string> {
  const heading = /^#\s+(.+?)\s*$/gm;
  const matches = [...source.matchAll(heading)];
  const sections: Record<string, string> = {};

  matches.forEach((match, index) => {
    const start = (match.index ?? 0) + match[0].length;
    const end = matches[index + 1]?.index ?? source.length;
    sections[match[1].trim()] = source.slice(start, end).trim();
  });
  return sections;
}

function toPlainText(source: string): string {
  return source
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/!\[[^\]]*\]\([^)]*\)/g, " ")
    .replace(/\[([^\]]+)\]\([^)]*\)/g, "$1")
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/[>*_~|-]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function createDescription(answer: string): string {
  const plain = toPlainText(answer);
  return plain.length > 112 ? `${plain.slice(0, 112).trim()}…` : plain;
}

let questionCache: Question[] | undefined;

export function getQuestions(): Question[] {
  if (questionCache) return questionCache;

  const catalog = loadYaml(
    fs.readFileSync(path.join(projectRoot, "catalog.yaml"), "utf8")
  ) as Catalog;

  const orderedIds: string[] = [];
  const metadata = new Map<string, CatalogEntry & { categories: string[] }>();

  Object.entries(catalog).forEach(([category, entries]) => {
    entries.forEach((entry) => {
      const existing = metadata.get(entry.id);
      if (existing) {
        existing.categories.push(category);
      } else {
        orderedIds.push(entry.id);
        metadata.set(entry.id, { ...entry, categories: [category] });
      }
    });
  });

  questionCache = orderedIds.map((id, index) => {
    const entry = metadata.get(id)!;
    const source = fs.readFileSync(path.join(projectRoot, "questions", `${id}.md`), "utf8");
    const sections = splitSections(source);
    const answer = sections["回答"] ?? "";
    const points = sections["面试考察点"] ?? "";
    const references = sections["参考资料"] ?? "";

    return {
      ...entry,
      index,
      answerHtml: markdown.render(answer),
      pointsHtml: markdown.render(points),
      referencesHtml: markdown.render(references),
      description: createDescription(answer),
      searchText: toPlainText(`${entry.title} ${entry.categories.join(" ")} ${source}`)
    };
  });

  return questionCache;
}

export function getCategories(): string[] {
  const categories = new Set<string>();
  getQuestions().forEach((question) => question.categories.forEach((category) => categories.add(category)));
  return [...categories];
}

export const difficultyLabels: Record<Difficulty, string> = {
  easy: "初级",
  medium: "中级",
  hard: "高级"
};
