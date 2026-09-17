// Deliberately placed under vendor/ so ingestion excludes the directory.
module.exports = function leftpad(value, width) {
  const text = String(value);
  return text.length >= width ? text : " ".repeat(width - text.length) + text;
};
