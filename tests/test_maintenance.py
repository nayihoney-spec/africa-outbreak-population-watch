import copy, importlib.util, json, pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('updater',ROOT/'scripts/update_data.py');u=importlib.util.module_from_spec(s);s.loader.exec_module(u)
class Maintenance(unittest.TestCase):
 def setUp(self):
  self.b=json.loads((ROOT/'data/published.json').read_text());self.sources=copy.deepcopy(self.b['verification']['sources']);self.now=self.b['verification']['checked_at']
 def test_reject_global_totals(self):
  raw='Total Cases (as of Oct. 14, 2026) 9,167 total confirmed cases and 4,413 total confirmed deaths Democratic Republic of the Congo <ul><li>9,144 confirmed cases</li><li>4,410 confirmed deaths</li></ul> Kenya 2 confirmed cases'
  x=u.parse_cdc(raw);self.assertEqual((x['cases'],x['deaths']),(9144,4410))
 def test_mismatch_preserves_original(self):
  before=copy.deepcopy(self.b);self.sources[1]['cases']+=1
  with self.assertRaises(ValueError):u.promote(self.b,self.sources,self.now)
  self.assertEqual(self.b,before)
 def test_reject_missing_country_block(self):
  with self.assertRaises(ValueError):u.parse_cdc('Total Cases (as of Oct. 14, 2026) 9167 confirmed cases')
 def test_reject_stale(self):
  for x in self.sources:x['report_as_of']='2000-01-01'
  with self.assertRaises(ValueError):u.promote(self.b,self.sources,self.now)
 def test_reject_count_regression(self):
  for x in self.sources:x['cases']=self.b['latest']['outbreaks'][-1]['cases']-1
  with self.assertRaises(ValueError):u.promote(self.b,self.sources,self.now)
 def test_reject_mixed_view_revision(self):
  self.b['outbreaks']['events'][-1]['cases']+=1
  with self.assertRaises(AssertionError):u.validate(self.b)
 def test_published_consistent(self):self.assertTrue(u.validate(self.b))
if __name__=='__main__':unittest.main()
