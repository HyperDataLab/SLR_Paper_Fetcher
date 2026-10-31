import { memo } from 'react';
import type { NodeProps } from '@xyflow/react';
import ResearchGraphNodeCard, { type ResearchGraphTone } from '../../graph-shared/ResearchGraphNodeCard';
import type { AifFlowNode } from '../types/aif.types';
import NodeHandles from './NodeHandles';

function nodeTone(role: string, informationRole: AifFlowNode['data']['informationRole']): ResearchGraphTone {
  if (role === 'claim' || role === 'evidence') return 'success';
  if (role === 'objection' || role === 'rebuttal') return 'danger';
  if (role === 'qualifier' || role === 'warrant') return 'warning';
  if (role === 'backing' || role === 'acknowledgment') return 'neutral';
  return informationRole === 'conclusion' ? 'success' : 'primary';
}

function InformationNode({ id, data, selected }: NodeProps<AifFlowNode>) {
  const node = { id, data } as AifFlowNode;
  const metadata = data.originalNode.metadata || {};
  const craftRole = String(metadata.craft_role || '').toLowerCase();
  const craftLabel = String(metadata.craft_label || '');
  const roleLabel = data.informationRole === 'premise-conclusion'
    ? 'Premise · Conclusion'
    : data.informationRole;
  const status = metadata.craft_missing ? 'not identified' : data.reviewStatus;

  return <ResearchGraphNodeCard
    role={craftLabel || roleLabel}
    text={data.text}
    status={String(status)}
    origin={String(metadata.assertion_origin || 'Explicit source').replaceAll('_', ' ')}
    note={data.groundedLabel || undefined}
    tone={nodeTone(craftRole, data.informationRole)}
    selected={selected}
  >
    <NodeHandles node={node} />
  </ResearchGraphNodeCard>;
}

export default memo(InformationNode);
