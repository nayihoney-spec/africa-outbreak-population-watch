import copy, importlib.util, json, pathlib, tempfile, unittest, sys
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
def module(name,file):
 s=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
sys.path.insert(0,str(ROOT/'scripts'))
u=module('updater','update_data.py')
a=module('advisories','update_advisories.py')
class AuditPreservation(unittest.TestCase):
 def test_success_preserves_pending_cloud_evidence_without_retimestamp(self):
  previous={'cloud_audit':{'checked_at':'old','counts':{'newer_official_snapshot_pending':{'cases':10414,'promoted':False}}},'last_successful_validation':{'checked_at':'old'},'advisory_status':'blocked','error':'old failure'}
  before=copy.deepcopy(previous); verification={'checked_at':'new','status':'verified'}
  result=u.maintenance_status(previous,{'status':'passed','checked_at':'new','published_changed':True},verification)
  self.assertEqual(previous,before);self.assertEqual(result['cloud_audit'],previous['cloud_audit']);self.assertEqual(result['last_successful_validation'],verification);self.assertNotIn('error',result);self.assertEqual(result['advisory_status'],'blocked')
 def test_failed_refresh_keeps_last_success_and_published_bytes(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=pathlib.Path(tmp);(root/'data').mkdir();bundle=(ROOT/'data/published.json').read_bytes();(root/'data/published.json').write_bytes(bundle)
   previous={'cloud_audit':{'checked_at':'old','pending':'INSP169'},'last_successful_validation':{'checked_at':'old','status':'verified'}}
   (root/'data/maintenance.json').write_text(json.dumps(previous))
   with patch.object(u,'ROOT',root),patch.object(u,'fetch',side_effect=ValueError('source unavailable')),patch('sys.argv',['update_data.py']):self.assertEqual(u.main(),1)
   result=json.loads((root/'data/maintenance.json').read_text());self.assertEqual(result['cloud_audit'],previous['cloud_audit']);self.assertEqual(result['last_successful_validation'],previous['last_successful_validation']);self.assertFalse(result['published_changed']);self.assertEqual((root/'data/published.json').read_bytes(),bundle)
 def test_advisory_review_survives_new_attempt(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=pathlib.Path(tmp);(root/'data').mkdir();prior={'cloud_review':{'checked_at':'old','manual_content_verified':['AU']},'blocked':{'AU':'old'}}
   (root/'data/advisory-maintenance.json').write_text(json.dumps(prior))
   with patch.object(a,'ROOT',root):result=a.preserve_review({'checked_at':'new','blocked':{'US':'403'},'passed':['AU']})
   self.assertEqual(result['cloud_review'],prior['cloud_review']);self.assertEqual(result['blocked'],{'US':'403'});self.assertEqual(result['checked_at'],'new')
 def test_no_success_is_invented_on_first_failed_check(self):
  self.assertNotIn('last_successful_validation',u.maintenance_status({}, {'status':'failed'}))
if __name__=='__main__':unittest.main()
