// Only recognize the exact, untouched starter code from version 0.1.
// Actual user-written programs remain verbatim, including whitespace.
const legacyStarters = new Set([
  "#include <stdio.h>\n\nint main(void) {\n    // 在这里编写你的程序\n    return 0;\n}",
  "#include <iostream>\n#include <vector>\n#include <algorithm>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    // 在这里编写你的程序\n    return 0;\n}",
  'import sys\n\n\ndef main():\n    data = sys.stdin.read()\n    # 在这里编写你的程序\n\n\nif __name__ == "__main__":\n    main()',
]);

export function restoreDraft(value) {
  if (typeof value !== "string") return "";
  return legacyStarters.has(value.replace(/\r\n/g, "\n").trim()) ? "" : value;
}
