"""Deterministic, dependency-free Stage06 reference interpreter for future UI wiring.
No inference from free text. Responses stay in the caller; nothing written to disk.
"""
import json,argparse
from pathlib import Path

def activity_run(activity,answers=None,skip_at_step=None):
    answers=answers or {}
    steps={x['id']:x for x in activity['steps']}
    cursor=activity['start_step_id'];visited=[];feedback=[];missing=[]
    while cursor not in activity['terminal_states']:
        if cursor in visited:raise ValueError('step cycle')
        if cursor not in steps:raise ValueError('missing step')
        if cursor==skip_at_step:return {'status':'skipped','visited':visited,'feedback':'Stopped at your choice. No explanation required.','event_type':'activity.skipped'}
        step=steps[cursor];visited.append(cursor);field=step['input']['field'];val=answers.get(field)
        if step['input']['required'] and (val is None or val==''):
            missing.append(field)
        if val is not None and step['input']['type']=='choice':
            choices=[v['value'] for v in step['input']['options']]
            if val not in choices:missing.append(field+' (invalid option)')
            if val in step.get('feedback',{}):feedback.append(step['feedback'][val])
        if isinstance(val,str) and step['input']['type']=='multiline_text':
            if len(val)>step['input'].get('max_chars',10**8) or len(val)<step['input'].get('min_chars',0):missing.append(field+' (text length)')
        cursor=step['navigation']['next']
    if missing:return {'status':'incomplete','visited':visited,'missing':missing,'feedback':'Complete or skip the listed fields; no personal interpretation is made.','event_type':None}
    if answers.get('observation_mode')=='declined':return {'status':'skipped','visited':visited,'feedback':'Declined without penalty.','event_type':'activity.skipped'}
    return {'status':'completed','visited':visited,'feedback':activity['feedback_policy']['final_feedback'],'choice_feedback':feedback,'event_type':'activity.completed'}

def scenario_run(scenario,choices,skip_at_node=None):
    nodes={x['id']:x for x in scenario['nodes']}
    cur=scenario['start_node'];path=[];reasons=[];i=0
    while True:
        if cur==skip_at_node:
            return {'status':'skipped','path':path+[scenario['exit_node']],'event_type':'scenario.skipped'}
        node=nodes[cur]
        path.append(cur)
        if node['type']=='safe_exit':return {'status':'skipped','path':path,'event_type':'scenario.skipped'}
        if node['type']=='outcome':return {'status':'completed','path':path,'outcome':node['hypothetical_consequence'],'tradeoff':node['tradeoff'],'reflection_prompt':node['reflection_prompt'],'decision_explanations':reasons,'event_type':'scenario.completed'}
        if i>=len(choices):return {'status':'incomplete','path':path,'prompt':node['prompt'],'options':[x['text'] for x in node['choices']]}
        ix=choices[i];i+=1
        if not isinstance(ix,int) or not 0<=ix<len(node['choices']):raise ValueError('invalid choice')
        choice=node['choices'][ix];reasons.append(choice['rationale']);cur=choice['target']
        if len(path)>len(nodes):raise ValueError('invalid graph path')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--mode',choices=['activity','scenario'],required=True);p.add_argument('--id',required=True);p.add_argument('--choices',default='0,0');a=p.parse_args()
 data=json.load(open(Path(a.root)/'data'/('PCI_EXECUTABLE_ACTIVITIES.json' if a.mode=='activity' else 'PCI_BRANCHING_SCENARIOS.json')))
 found=next((x for x in data if x['id']==a.id),None)
 if found is None:p.error('ID not found')
 if a.mode=='activity':
  fixture=json.load(open(Path(a.root)/'tests/PCI_ACTIVITY_SMOKE_FIXTURES.json'))
  obj=next(x['response'] for x in fixture if x['target_id']==a.id)
  result=activity_run(found,obj)
 else:result=scenario_run(found,[int(v) for v in a.choices.split(',')])
 print(json.dumps(result,indent=2))
