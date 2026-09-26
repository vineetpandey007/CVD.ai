import { useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";

interface FadeInProps {
  children: ReactNode;
  /** stagger delay in ms, applied when entering — not applied on exit */
  delay?: number;
  className?: string;
}

/**
 * Fades and rises content in when it scrolls into view, and fades it back
 * out when it scrolls out of view — in either direction. Respects
 * prefers-reduced-motion by staying fully visible with no animation.
 */
export function FadeIn({ children, delay = 0, className = "" }: FadeInProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setVisible(true);
      return;
    }

    const node = ref.current;
    if (!node) return;

    let showTimer: ReturnType<typeof setTimeout>;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          showTimer = setTimeout(() => setVisible(true), delay);
        } else {
          clearTimeout(showTimer);
          setVisible(false);
        }
      },
      { threshold: 0.15, rootMargin: "0px 0px -40px 0px" }
    );

    observer.observe(node);
    return () => {
      observer.disconnect();
      clearTimeout(showTimer);
    };
  }, [delay]);

  return (
    <div
      ref={ref}
      className={`transition-all duration-700 ease-out ${
        visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"
      } ${className}`}
    >
      {children}
    </div>
  );
}
