from knowledge.retrieval import fuse

def test_fusion_deduplicates_candidates_and_rewards_agreement():
 a=dict(id="a");b=dict(id="b");c=dict(id="c")
 out=fuse([(a,100),(b,1)],[(c,.99),(b,.1)])
 assert out[0][0]["id"]=="b" and len(out)==3
 assert fuse([],[])==[]
