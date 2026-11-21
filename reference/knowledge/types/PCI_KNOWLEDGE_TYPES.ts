/* PCI Stage05 types. Source statuses describe the text, never therapeutic efficacy. */
export type ClaimStatus = 'verified_in_pdf' | 'provisional' | 'not_located' | 'incomplete';
export type EvidenceStatus = 'book_assertion_only' | 'corroborated_external' | 'disputed' | 'not_assessed';
export type RelationshipType = 'supports'|'qualifies'|'contradicts'|'complements'|'requires'|'alternative_explanation'|'ethical_tension';
export type CoverageState = 'indexed'|'substantive'|'partial'|'unprocessed';
export type ExerciseOrigin = 'book'|'updated_edition_editor'|'PCI_adaptation'|'uncertain';
export type RecordType = 'book'|'chapter'|'section'|'coverage'|'issue'|'concept'|'claim'|'mechanism'|'author_practice'|'anecdote'|'evidence_assessment'|'application'|'exercise'|'citation'|'relationship';
export interface SourcePage { source_id: string; pdf_page: number; printed_page: number|null; edition_id: string; source_sha256: string; }
export interface CanonicalRecord { id:string; type: RecordType; chapter_id:string|null; title:string; content:string; source_type:string; source_status:ClaimStatus; evidence_status:EvidenceStatus; source_refs:SourcePage[]; content_owner:string; provenance: Record<string,unknown>; revision:Record<string,unknown>; [key:string]:unknown; }
export interface PCIConcept extends CanonicalRecord {type:'concept'; thesis:string; substantive_paraphrase:string; claim_ids?: string[]; case_ids?:string[]; practice_ids?:string[]; }
export interface PCIClaim extends CanonicalRecord {type:'claim'; concept_id?:string; empirical_proof_status?:string; }
export interface PCIAuthorPractice extends CanonicalRecord {type:'author_practice'; instructions:string[]; timing_as_printed_or_paraphrased:string; frequency_per_week?:number|null; program_days?:number|null; }
export interface PCIRelationship extends CanonicalRecord {type:'relationship';from_id:string;to_id:string;relationship_type:RelationshipType;supporting_source_refs:SourcePage[];rationale:string;}
export interface PCISearchDocument {id:string; type:RecordType; title:string; chapter_id:string|null; pdf_pages:number[];source_status:ClaimStatus;evidence_status:EvidenceStatus;themes:string[];search_terms:string;destination_id:string;preview:string;source_pack:string;}
export type PCITable<T extends CanonicalRecord = CanonicalRecord> = T[];
export interface PCIUserDataExport {format_version:string; exported_at:string; app_schema_version:string; private_entries:unknown[];}
/* Do not store private journals inside public canonical JSON. Persist private state in IndexedDB and encrypted/local versioned export. */
