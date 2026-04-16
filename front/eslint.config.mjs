import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  {
    settings: {
      react: {
        version: "19.2",
      },
    },
    rules: {
      // Nommage Intention→Résultat : avertir sur les identifiants trop courts
      // Exceptions : t (next-intl), i (index de boucle), e (event local)
      "id-length": ["warn", { min: 2, exceptions: ["t", "i", "e"] }],
    },
  },
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
  ]),
]);

export default eslintConfig;
