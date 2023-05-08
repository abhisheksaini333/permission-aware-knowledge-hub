from knowledge.evaluation import summarize

def test_report_keeps_quality_latency_and_errors_visible():
 rows=[dict(mode="lexical",recall_at_3=1.,reciprocal_rank=1.,exact_match=0.,token_f1=.5,correct_abstention=None,retrieval_ms=2.,answer_ms=5.,error=None),dict(mode="lexical",recall_at_3=None,reciprocal_rank=None,exact_match=None,token_f1=None,correct_abstention=1.,retrieval_ms=4.,answer_ms=9.,error=None)]
 s=summarize(rows)["lexical"]
 assert s["retrieval"]["recall_at_3"]==1 and s["answer"]["exact_match"]==0
 assert s["latency"]["answer_p95_ms"]==9 and s["cases"]==2
