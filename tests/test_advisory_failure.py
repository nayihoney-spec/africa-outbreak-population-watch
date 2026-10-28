import contextlib,copy,importlib.util,io,json,pathlib,sys,tempfile,unittest,urllib.error
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('advisory_failure_updater',ROOT/'scripts/update_advisories.py')
advisories=importlib.util.module_from_spec(spec);spec.loader.exec_module(advisories)
class AdvisoryFailure(unittest.TestCase):
 def test_urlopen_timeout_preserves_verified_alert_and_browser_safe_bundle(self):
  before=json.loads((ROOT/'data/published.json').read_text())
  with tempfile.TemporaryDirectory() as folder:
   root=pathlib.Path(folder);(root/'data').mkdir();(root/'data/published.json').write_text(json.dumps(before))
   with patch.object(advisories,'ROOT',root),patch.object(advisories,'extract',side_effect=urllib.error.URLError('timed out')),contextlib.redirect_stdout(io.StringIO()):
    self.assertEqual(advisories.main(),1)
   after=json.loads((root/'data/published.json').read_text())
   rows={r['code']:r for r in after['advisories']['items']}
   for previous in before['advisories']['items']:
    if previous['code'] not in advisories.PARSERS:continue
    row=rows[previous['code']]
    for key in ['level','evidence','verified_at','source_published_at','source_updated_at']:
     self.assertEqual(row.get(key),previous.get(key))
    self.assertEqual(row['last_attempt_status'],'blocked')
    self.assertEqual(row['last_attempt_error'],'[urlopen error timed out]')
   self.assertEqual(after['verification'],before['verification'])
   def check(value):
    if isinstance(value,str):self.assertNotRegex(value,r'[<>\x00]')
    elif isinstance(value,list):
     for item in value:check(item)
    elif isinstance(value,dict):
     for item in value.values():check(item)
   check(after)
if __name__=='__main__':unittest.main()
