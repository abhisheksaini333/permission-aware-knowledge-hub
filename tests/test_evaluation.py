from knowledge.evaluation import retrieval_metrics,answer_metrics

def test_retrieval_recall_and_reciprocal_rank():
 m=retrieval_metrics([{"source":"wrong"},{"source":"right"}],"right")
 assert m=={"recall_at_3":1.0,"reciprocal_rank":.5}
 assert retrieval_metrics([],"right")["recall_at_3"]==0

def test_answer_exact_match_f1_and_abstention_are_distinct():
 a=answer_metrics("seven days",False,"seven days")
 assert a["exact_match"]==1 and a["token_f1"]==1 and a["correct_abstention"] is None
 assert answer_metrics("No supported answer",True,None)["correct_abstention"]==1
 assert answer_metrics("seven days",False,None)["correct_abstention"]==0
