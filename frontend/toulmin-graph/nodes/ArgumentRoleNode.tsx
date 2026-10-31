import { memo, useLayoutEffect } from 'react';
import { Handle, Position, useUpdateNodeInternals, type NodeProps } from '@xyflow/react';
import ResearchGraphNodeCard, { type ResearchGraphTone } from '../../graph-shared/ResearchGraphNodeCard';
import type { ToulminFlowNode, ToulminNodeData, ToulminNodeType } from '../types/toulmin.types';

type RoleNodeProps = NodeProps<ToulminFlowNode> & { role: ToulminNodeType };

function toneForRole(role: ToulminNodeType): ResearchGraphTone {
  if (role === 'claim') return 'success';
  if (role === 'rebuttal') return 'danger';
  if (role === 'qualifier') return 'warning';
  if (role === 'backing') return 'neutral';
  return 'primary';
}

function AllSideHandles({ role, data }: { role: ToulminNodeType; data: ToulminNodeData }) {
  const handles: Array<{ id: string; type: 'source' | 'target'; position: Position; style?: React.CSSProperties }> = [];
  if (role === 'grounds') {
    handles.push(
      { id: 'out-right', type: 'source', position: Position.Right },
      { id: 'out-left', type: 'source', position: Position.Left },
      { id: 'out-bottom', type: 'source', position: Position.Bottom },
    );
  } else if (role === 'claim') {
    for (let index = 0; index < (data.groundPortCount || 0); index++) {
      handles.push({ id: `in-ground-${index}`, type: 'target', position: Position.Left, style: { top: `${((index + 1) / ((data.groundPortCount || 0) + 1)) * 55}%` } });
      handles.push({ id: `in-ground-outer-${index}`, type: 'target', position: Position.Right, style: { top: `${20 + ((index + 1) / ((data.groundPortCount || 0) + 1)) * 60}%` } });
    }
    handles.push({ id: 'in-left', type: 'target', position: Position.Left });
    for (let index = 0; index < (data.rebuttalPortCount || 0); index++) handles.push({ id: `in-rebuttal-${index}`, type: 'target', position: Position.Bottom, style: { left: `${(0.68 + ((index + 1) / ((data.rebuttalPortCount || 0) + 1)) * 0.22) * 100}%` } });
    for (let index = 0; index < (data.warrantPortCount || 0); index++) handles.push({ id: `in-warrant-${index}`, type: 'target', position: Position.Bottom, style: { left: `${(0.12 + ((index + 1) / ((data.warrantPortCount || 0) + 1)) * 0.28) * 100}%` } });
    for (let index = 0; index < (data.qualifierPortCount || 0); index++) handles.push({ id: `in-qualifier-${index}`, type: 'target', position: Position.Left, style: { top: `${58 + ((index + 1) / ((data.qualifierPortCount || 0) + 1)) * 22}%` } });
  } else if (role === 'warrant') {
    handles.push({ id: 'out-top', type: 'source', position: Position.Top }, { id: 'out-right', type: 'source', position: Position.Right }, { id: 'in-bottom', type: 'target', position: Position.Bottom });
    for (let index = 0; index < (data.backingPortCount || 0); index++) handles.push({ id: `in-backing-${index}`, type: 'target', position: Position.Bottom, style: { left: `${(0.1 + ((index + 1) / ((data.backingPortCount || 0) + 1)) * 0.8) * 100}%` } });
  } else if (role === 'backing') {
    handles.push({ id: 'out-top', type: 'source', position: Position.Top }, { id: 'out-right', type: 'source', position: Position.Right }, { id: 'in-bottom', type: 'target', position: Position.Bottom });
  } else if (role === 'qualifier') {
    handles.push({ id: 'out-right', type: 'source', position: Position.Right });
  } else if (role === 'rebuttal') {
    handles.push({ id: 'out-top', type: 'source', position: Position.Top }, { id: 'out-right', type: 'source', position: Position.Right });
  }
  return <>{handles.map((handle) => <Handle key={handle.id} id={handle.id} type={handle.type} position={handle.position} isConnectable={false} style={{ ...handle.style, opacity: 0, width: 7, height: 7, background: 'currentColor', border: 0 }} />)}</>;
}

function ArgumentRoleNode({ id, data, selected, role }: RoleNodeProps) {
  const updateNodeInternals = useUpdateNodeInternals();
  useLayoutEffect(() => {
    updateNodeInternals(id);
  }, [id, updateNodeInternals, data.groundPortCount, data.warrantPortCount, data.backingPortCount, data.qualifierPortCount, data.rebuttalPortCount]);

  const origin = data.origin === 'inferred' ? 'AI reconstructed' : data.origin === 'hypothetical' ? 'Hypothetical' : 'Explicit source';
  const page = data.sourceReference?.page ? `Page ${String(data.sourceReference.page)}` : undefined;
  return <ResearchGraphNodeCard
    role={data.label.split('·')[0].trim()}
    text={data.text}
    status={data.reviewStatus}
    origin={origin}
    note={page}
    tone={toneForRole(role)}
    selected={selected}
  >
    <AllSideHandles role={role} data={data} />
  </ResearchGraphNodeCard>;
}

export default memo(ArgumentRoleNode);
