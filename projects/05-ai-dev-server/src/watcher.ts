import chokidar from "chokidar";

export function createWatcher(targetPath: string, onChange: () => void) {
  const watcher = chokidar.watch(targetPath, {
    ignoreInitial: true,
    ignored: ["**/node_modules/**", "**/.git/**", "**/dist/**"],
  });

  watcher.on("change", onChange);
  return watcher;
}
