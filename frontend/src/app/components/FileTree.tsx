import { useMemo } from "react";

import type { FileTreeNode } from "../fileTree";
import { buildFileTree, fileExtension, fileStem } from "../fileTree";

type FileTreeViewProps = {
  paths: readonly string[];
};

export function FileTreeView({ paths }: FileTreeViewProps) {
  const tree = useMemo(() => buildFileTree(paths), [paths]);
  if (tree.length === 0) {
    return <p className="text-muted small mb-0 px-2 py-2">No matching files.</p>;
  }
  return (
    <ul className="file-tree">
      {tree.map((node) => (
        <FileTreeItem key={`${node.kind}:${node.path}`} node={node} />
      ))}
    </ul>
  );
}

function FileTreeItem({ node }: { node: FileTreeNode }) {
  if (node.kind === "dir") {
    return (
      <li className="file-tree-dir">
        <details open>
          <summary className="file-tree-dir-name" title={node.path}>
            {node.name}
          </summary>
          {node.children.length > 0 ? (
            <ul className="file-tree">
              {node.children.map((child) => (
                <FileTreeItem
                  key={`${child.kind}:${child.path}`}
                  node={child}
                />
              ))}
            </ul>
          ) : null}
        </details>
      </li>
    );
  }

  const extension = fileExtension(node.name);
  const stem = fileStem(node.name);
  return (
    <li>
      <span className="file-tree-file" title={node.path}>
        <span className="file-tree-stem">{stem}</span>
        {extension ? <span className="file-tree-ext">{extension}</span> : null}
      </span>
    </li>
  );
}
