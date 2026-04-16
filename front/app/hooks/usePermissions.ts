import { useState, useCallback } from "react";
import { api } from "../lib/api";
import type { PermissionsMap, PermissionStatus, Organization } from "../types";

export function usePermissions() {
  const [permissions, setPermissions] = useState<PermissionsMap>({});
  const [loadingPermissions, setLoadingPermissions] = useState(false);
  const [organization, setOrganization] = useState<Organization | null>(null);

  const resetPermissions = useCallback(() => {
    setPermissions({});
    setOrganization(null);
  }, []);

  const fetchPermissions = useCallback(async (urls: string[]) => {
    const validUrls = urls.filter(Boolean);
    if (validUrls.length === 0) return;
    setLoadingPermissions(true);
    try {
      const permissionsHttpResponse = await api.permissions(validUrls);
      if (!permissionsHttpResponse.ok) return;
      const permissionsResult = await permissionsHttpResponse.json();
      const docs: Array<{ url: string; isPermitted: boolean; formats?: string[] }> | null =
        permissionsResult?.data?.docs ?? null;
      const org: Organization | null = permissionsResult?.data?.organization ?? null;
      const purchased: boolean = org?.purchased ?? false;
      setOrganization(org);
      const permissionsMap: PermissionsMap = {};
      // Initialise toutes les URLs à unknown — fallback pour les réponses partielles
      validUrls.forEach((url) => {
        permissionsMap[url] = { status: "unknown" as PermissionStatus, formats: [] };
      });
      if (docs) {
        docs.forEach(({ url, isPermitted, formats }) => {
          const status: PermissionStatus = !isPermitted ? "restricted" : purchased ? "institutional" : "open";
          permissionsMap[url] = { status, formats: formats ?? [] };
        });
      }
      setPermissions(permissionsMap);
    } catch {
      // Échec silencieux — les badges restent en état neutre
    } finally {
      setLoadingPermissions(false);
    }
  }, []);

  return { permissions, loadingPermissions, organization, fetchPermissions, resetPermissions };
}
