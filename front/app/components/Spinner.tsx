"use client";

type SpinnerSize = "sm" | "md" | "lg";
type SpinnerColor = "white" | "highlight";

interface SpinnerProps {
  size?: SpinnerSize;
  color?: SpinnerColor;
}

const SIZE_CLASSES: Record<SpinnerSize, string> = {
  sm: "w-3 h-3 border-2",
  md: "w-4 h-4 border-2",
  lg: "w-5 h-5 border-2",
};

const COLOR_CLASSES: Record<SpinnerColor, string> = {
  white: "border-white/40 border-t-white",
  highlight: "border-highlight border-t-transparent",
};

export default function Spinner({ size = "md", color = "white" }: SpinnerProps) {
  return (
    <div
      className={`${SIZE_CLASSES[size]} ${COLOR_CLASSES[color]} rounded-full animate-spin`}
    />
  );
}
