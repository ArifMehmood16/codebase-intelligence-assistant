export type FileTreeKind = "dir" | "file";

export type FileTreeNode = {
  name: string;
  path: string;
  kind: FileTreeKind;
  children: FileTreeNode[];
};

export function fileName(path: string): string {
  const trimmed = path.replace(/\/+$/, "");
  const parts = trimmed.split("/").filter((part) => part.length > 0);
  return parts[parts.length - 1] ?? trimmed;
}

export function fileExtension(name: string): string {
  const lastDot = name.lastIndexOf(".");
  if (lastDot <= 0 || lastDot === name.length - 1) {
    return "";
  }
  return name.slice(lastDot);
}

export function fileStem(name: string): string {
  const extension = fileExtension(name);
  return extension ? name.slice(0, -extension.length) : name;
}

export function buildFileTree(paths: readonly string[]): FileTreeNode[] {
  const root: FileTreeNode = {
    name: "",
    path: "",
    kind: "dir",
    children: [],
  };

  const unique = [...new Set(paths.filter((path) => path.trim().length > 0))];
  unique.sort((left, right) => left.localeCompare(right));

  for (const raw of unique) {
    const isDirectory = raw.endsWith("/");
    const normalized = raw.replace(/\/+$/, "");
    const parts = normalized.split("/").filter((part) => part.length > 0);
    let current = root;
    let accumulated = "";

    parts.forEach((part, index) => {
      accumulated = accumulated ? `${accumulated}/${part}` : part;
      const isLast = index === parts.length - 1;
      const kind: FileTreeKind = isLast && !isDirectory ? "file" : "dir";
      let child = current.children.find(
        (node) => node.name === part && node.kind === kind,
      );
      if (!child) {
        child = {
          name: part,
          path: accumulated,
          kind,
          children: [],
        };
        current.children.push(child);
      }
      current = child;
    });
  }

  sortTree(root);
  return root.children;
}

function sortTree(node: FileTreeNode): void {
  node.children.sort((left, right) => {
    if (left.kind !== right.kind) {
      return left.kind === "dir" ? -1 : 1;
    }
    return left.name.localeCompare(right.name);
  });
  for (const child of node.children) {
    sortTree(child);
  }
}
