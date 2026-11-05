import { EditorView } from "codemirror";
import { HighlightStyle, syntaxHighlighting } from "@codemirror/language";
import { tags } from "@lezer/highlight";
import "./theme.css";

const darkHighlight = HighlightStyle.define([
  {
    tag: [tags.keyword, tags.modifier, tags.bool, tags.null],
    color: "#c9a7ff",
  },
  { tag: tags.string, color: "#9edb9e" },
  { tag: tags.number, color: "#edbd87" },
  { tag: [tags.typeName, tags.className], color: "#79d7d0" },
  { tag: tags.function(tags.variableName), color: "#e5d08c" },
  { tag: [tags.variableName, tags.propertyName], color: "#dddddd" },
  { tag: tags.comment, color: "#878787", fontStyle: "italic" },
  { tag: tags.meta, color: "#9dc5ff" },
  { tag: [tags.operator, tags.punctuation, tags.bracket], color: "#bcbcbc" },
]);

export function editorAppearance() {
  return [
    EditorView.theme(
      {
        "&": {
          height: "100%",
          fontSize: "13px",
          backgroundColor: "#000000",
          color: "#dddddd",
        },
        ".cm-scroller": {
          fontFamily: '"SFMono-Regular",Consolas,"Liberation Mono",monospace',
        },
        ".cm-content": {
          padding: "18px 0",
          caretColor: "#ffffff",
        },
        ".cm-cursor, .cm-dropCursor": {
          borderLeftColor: "#ffffff",
        },
        ".cm-gutters": {
          backgroundColor: "#000000",
          borderRight: "1px solid #242424",
          color: "#6c6c6c",
        },
        ".cm-activeLine, .cm-activeLineGutter": {
          backgroundColor: "#101010",
        },
        ".cm-selectionBackground, &.cm-focused .cm-selectionBackground": {
          backgroundColor: "#18395d",
        },
        ".cm-tooltip": {
          backgroundColor: "#000000",
          color: "#dddddd",
          border: "1px solid #333333",
        },
        "&.cm-focused": { outline: "none" },
      },
      { dark: true },
    ),
    syntaxHighlighting(darkHighlight),
  ];
}
