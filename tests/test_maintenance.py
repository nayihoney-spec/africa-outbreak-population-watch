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
 def test_ecdc_multi_country_page_keeps_drc_scope_and_dates(self):
  raw='As of 22 October, in Kenya, a total of nine confirmed cases, including one death. As of 21 October 2026, the <a>Democratic Republic of the Congo</a> (DRC) has reported a total of 9 704 confirmed cases, including 4 687 related deaths (from data up until 20 October).'
  x=u.parse_ecdc(raw)
  self.assertEqual((x['cases'],x['deaths']),(9704,4687))
  self.assertEqual((x['report_as_of'],x['data_through']),('2026-10-21','2026-10-20'))
 def test_ecdc_legacy_wording_remains_supported(self):
  x=u.parse_ecdc('As of 19 October 2026, the Democratic Republic of the Congo (DRC) reported a total of 9 552 confirmed cases, including 4 602 related deaths (from data up until 18 October)')
  self.assertEqual((x['cases'],x['deaths'],x['data_through']),(9552,4602,'2026-10-18'))
 def test_ecdc_foreign_and_unconfirmed_totals_are_rejected(self):
  for raw in ('As of 21 October 2026, Kenya has reported a total of 9 704 confirmed cases, including 4 687 related deaths', 'As of 21 October 2026, the Democratic Republic of the Congo (DRC) has reported a total of 9 704 suspected cases, including 4 687 related deaths'):
   with self.assertRaises(ValueError):u.parse_ecdc(raw)
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
 def test_primary_date_matches_cdc(self):
  result=u.promote(self.b,self.sources,self.now)
  self.assertEqual(result['latest']['outbreaks'][-1]['as_of'],self.sources[0]['report_as_of'])
 def test_published_consistent(self):self.assertTrue(u.validate(self.b))
if __name__=='__main__':unittest.main()
