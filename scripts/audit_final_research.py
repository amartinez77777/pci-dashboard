#!/usr/bin/env python3
"""Stage final inherited research quality audit; DOES NOT verify source PDF images."""
import json,glob,collections,hashlib,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];DATA=R/'public/data';A=R/'audit/final';A.mkdir(parents=True,exist_ok=True)
load=lambda pat:[r for f in sorted(DATA.glob(pat)) for r in json.loads(f.read_text())]
concepts=load('concepts/*.json'); chapters=json.loads((DATA/'chapter-index.json').read_text())
index=json.loads((DATA/'concept-index.json').read_text());practice=json.loads((DATA/'practice-attribution.json').read_text());rels=load('relationships/*.json');acts=load('activities/*.json');scenarios=load('scenarios/*.json')
curriculum=json.loads((DATA/'curriculum.json').read_text())
ids={c['id'] for c in concepts};chapter_ids={c['id'] for c in chapters};activity_ids={a['id'] for a in acts};scenario_ids={s['id'] for s in scenarios}
rehearsal_file=json.loads((DATA/'rehearsals.json').read_text());rehearsal_ids={x['id'] for x in rehearsal_file} if isinstance(rehearsal_file,list) else set()
errors=[]
def check(condition,msg):
 if not condition:errors.append(msg)
check(len(chapters)==16 and len(chapter_ids)==16,'Chapter cardinality / IDs inconsistent')
check(len(concepts)==201 and len(ids)==201,'Concept cardinality / IDs inconsistent')
check(len(index)==201 and {r['id'] for r in index}==ids,'Concept index does not match full records')
check(len(acts)==32 and len(activity_ids)==32,'Activity ID/cardinality inconsistency')
check(len(scenarios)==16 and len(scenario_ids)==16,'Scenario ID/cardinality inconsistency')
check(len(rels)==109,'Graph edge count unexpected')
check(len(curriculum['days'])==21 and len({d['id'] for d in curriculum['days']})==21,'21-day authored curriculum mismatch')
check(set(curriculum['checkpoint_days'])=={4,9,15,21},'Checkpoint days mismatch')
check(len(practice)==70,'Original practice index count unexpected')
for c in concepts:
 check(c['chapter_id'] in chapter_ids,f"Missing chapter for concept {c['id']}")
 for ref in c.get('source_refs',[]):check(isinstance(ref.get('pdf_page'),int) and 1<=ref['pdf_page']<=332,f"Missing/inconsistent PDF locator for {c['id']}")
for a in acts:
 check(a['chapter_id'] in chapter_ids,f"Missing chapter for activity {a['id']}")
 for id in a.get('concept_ids',[]):check(id in ids,f"Missing concept {id} in {a['id']}")
for s in scenarios:
 check(s['chapter_id'] in chapter_ids,f"Missing chapter for scenario {s['id']}")
 for id in s.get('linked_concept_ids',[]):check(id in ids,f"Missing concept {id} in {s['id']}")
for d in curriculum['days']:
 for k,known in [('primary_concept_id',ids),('primary_activity_id',activity_ids),('optional_rehearsal_id',rehearsal_ids)]:
  v=d.get(k)
  if v:check(v in known,f"Broken {k} reference {v} in {d['id']}")
for r in rels:
 for k in ('source_concept_id','target_concept_id','from_concept_id','to_concept_id'):
  if r.get(k):check(r[k] in ids,f"Missing graph endpoint {k} in {r['id']}")
by_id={r['id']:r for r in concepts}
proposals={
'PCI-C-CH01-001':'The working self-description may influence choices, but it does not control every action; resources, environment and prior learning also matter.',
'PCI-C-CH01-005':'An altered appearance does not reliably produce an altered self-image; neither surgery nor self-reflection is a stand-alone treatment for body-image distress.',
'PCI-C-CH02-001':'The book’s built-in success instinct is an analogy for goal pursuit, not a literal internal device or guarantee of achievement.',
'PCI-C-CH02-002':'The proposed sequence from decision to imagination to action is not an established neural circuit; planning and learning offer more limited accounts.',
'PCI-C-CH03-002':'Visualizing an event is not equivalent to actually performing it; claims that the nervous system makes no distinction are overstated.',
'PCI-C-CH03-004':'Hypnosis anecdotes do not establish reliable surgical pain control; suggestions and attention cannot replace anesthesia or clinical care.',
'PCI-C-CH03-007':'Relief of perceived stress or pain is not evidence of faster tissue repair; never use imagery as a substitute for medical treatment.',
'PCI-C-CH04-006':'A reported grip-strength change under suggestion does not prove skill was magically unlocked; effort, measurement and demand effects remain plausible.',
'PCI-C-CH07-002':'A positive mood must not be portrayed as the sole cause of good health or a cure for illness; medical treatment and other factors matter.',
'PCI-C-CH08-002':'The SUCCESS mnemonic is a teaching framework, not a diagnostic personality score or moral ranking.',
'PCI-C-CH10-001':'An emotional scar is the author’s metaphor for guarded responses, not literal scar tissue or a mental-health diagnosis.',
'PCI-C-CH12-006':'Relaxation can be an optional coping response but cannot guarantee relief from trauma, panic or all anxiety.',
'PCI-C-CH14-009':'Historical engram explanations should not be treated as current definitive neuroscience; the text combines neurobiology with speculation.',
'PCI-C-CH15-005':'The life-force healing analogy does not establish that imagery or faith cures disease; biological recovery can have multiple causes.',
'PCI-C-CH15-008':'Reported placebo examples without verified study protocols do not establish clinical cure or justify stopping conventional treatment.',
'PCI-C-CH16-006':'An attributed recovery story cannot prove causation or imply that people with disabilities are responsible for their health outcomes.'
}
assert len(proposals)==16 and set(proposals).issubset(ids)
for c in concepts:check(c.get('evidence_status')!='independently_verified',f"Unexpected independent support claim: {c['id']}")
fields=['conditions_and_limits','ethical_clinical_cautions','common_misreading','alternative_explanation']
distribution={f:{'unique':len(set(str(c.get(f)) for c in concepts)),'largest_repeated_group':max(collections.Counter(str(c.get(f)) for c in concepts).values())} for f in fields}
identical=sum(c.get('conditions_and_limits')==c.get('ethical_clinical_cautions') for c in concepts)
output={
 'scope':'INHERITED RESEARCH CONTENT ONLY; target edition PDF not supplied with this release request; page images NOT rechecked',
 'status':'PASS' if not errors else 'FAIL',
 'counts':{'chapters':len(chapters),'concepts':len(concepts),'index_entries':len(index),'activities':len(acts),'scenarios':len(scenarios),'relationships':len(rels),'book_practices':len(practice),'curriculum_days':len(curriculum['days'])},
 'field_distribution':distribution,
 'same_text_in_limits_and_clinical_cautions':identical,
 'same_text_in_limits_and_clinical_cautions_percent':round(100*identical/len(concepts),1),
 'evidence_status_counts':dict(collections.Counter(c.get('evidence_status','unknown') for c in concepts)),
 'source_status_counts':dict(collections.Counter(c.get('source_status','unknown') for c in concepts)),
 'issues':errors,
 'priority_review':[{'id':id,'title':by_id[id]['title'],'inherited_source_locator':by_id[id]['source_refs'][0] if by_id[id].get('source_refs') else None,'original_common_misreading':by_id[id].get('common_misreading'),'proposed_specific_caution_NOT_CANONICAL':replacement,'rationale_from_inherited_record':{'thesis':by_id[id].get('thesis'),'conditions_and_limits':by_id[id].get('conditions_and_limits'),'alternative_explanation':by_id[id].get('alternative_explanation')},'publication_status':'editorial proposal only; requires PDF source re-review before canonical replacement'} for id,replacement in proposals.items()],
 'remaining_debt':{'concepts_without_nonredundant_clinical_cautions':identical,'concepts_without_individually_reviewed_common_misreading':len(concepts)-len(proposals),'pdf_image_verified_this_stage':0},
 'changes_to_canonical_research':0,
 'note':'Prior reports described identical conditions_and_limits across concepts; this audit shows those 201 entries are distinct. The duplicated fields are conditions_and_limits vs ethical_clinical_cautions WITHIN each record.'
}
(A/'RESEARCH_INTEGRITY_AUDIT.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':output['status'],'counts':output['counts'],'field_distribution':distribution,'same_cautions':identical,'link_errors':len(errors),'priority_review':len(proposals)},indent=2))
if errors:print('\n'.join(errors[:20]));raise SystemExit(1)
