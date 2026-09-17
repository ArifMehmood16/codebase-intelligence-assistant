import { describe, expect, it } from "vitest";

import {
  buildFileTree,
  fileExtension,
  fileName,
  fileStem,
} from "../../src/app/fileTree";

describe("file name helpers", () => {
  it("keeps the basename and extension when the path is nested", () => {
    expect(fileName("src/api/OwnerController.java")).toBe(
      "OwnerController.java",
    );
    expect(fileStem("OwnerController.java")).toBe("OwnerController");
    expect(fileExtension("OwnerController.java")).toBe(".java");
  });

  it("does not treat a leading dotfile as an extension-only name", () => {
    expect(fileStem(".gitignore")).toBe(".gitignore");
    expect(fileExtension(".gitignore")).toBe("");
  });
});

describe("buildFileTree", () => {
  it("nests indexed paths into directories with files as leaves", () => {
    const tree = buildFileTree([
      "README.md",
      "src/api/handlers.py",
      "src/app.py",
    ]);

    expect(tree.map((node) => node.name)).toEqual(["src", "README.md"]);
    expect(tree[0]).toMatchObject({
      kind: "dir",
      path: "src",
    });
    expect(tree[0]?.children.map((node) => node.name)).toEqual([
      "api",
      "app.py",
    ]);
    expect(tree[0]?.children[0]).toMatchObject({
      kind: "dir",
      path: "src/api",
    });
    expect(tree[0]?.children[0]?.children).toEqual([
      {
        name: "handlers.py",
        path: "src/api/handlers.py",
        kind: "file",
        children: [],
      },
    ]);
    expect(tree[1]).toMatchObject({
      name: "README.md",
      path: "README.md",
      kind: "file",
    });
  });

  it("sorts directories before files and names alphabetically within each kind", () => {
    const tree = buildFileTree(["b.py", "a.py", "src/x.py", "lib/y.py"]);
    expect(tree.map((node) => `${node.kind}:${node.name}`)).toEqual([
      "dir:lib",
      "dir:src",
      "file:a.py",
      "file:b.py",
    ]);
  });
});
