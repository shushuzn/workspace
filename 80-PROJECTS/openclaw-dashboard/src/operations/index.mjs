/**
 * Operations Index
 * Factory for all operations
 */

import { GenDashboardData, WorkspaceAutoCommit, CreateMissingReadme,
         FindWorkspaceIssues, CleanRecordedIssues, SyncProjectMarkers } from './productive-ops.mjs';
import { CheckProjectReadmes, CheckMemorySize, BrainstormProjects,
         FindLargeFiles, CheckGitRemotes } from './detection-ops.mjs';

export function getAllOperations(workspace) {
  return [
    new GenDashboardData(workspace),
    new WorkspaceAutoCommit(workspace),
    new CheckProjectReadmes(workspace),
    new CheckMemorySize(workspace),
    new BrainstormProjects(workspace),
    new CreateMissingReadme(workspace),
    new FindLargeFiles(workspace),
    new FindWorkspaceIssues(workspace),
    new CleanRecordedIssues(workspace),
    new CheckGitRemotes(workspace),
    new SyncProjectMarkers(workspace),
  ];
}

export { DetectionOperation, ProductiveOperation } from './base.mjs';
