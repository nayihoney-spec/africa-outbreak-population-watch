import importlib.util,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
s=importlib.util.spec_from_file_location('alerts',ROOT/'scripts/update_advisories.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
class OfficialAlertFields(unittest.TestCase):
 def test_boca_alert_date_not_footer(self):
  html='<table><tr><th>發布/更新日期</th><td>2026-08-31</td></tr><tr><th>警示等級</th><td><span></span>第四級：紅色儘速離境</td></tr><tr><th>國家地區</th><td>剛果民主共和國</td></tr></table><footer>更新日期：2022-06-21</footer>'
  result=a.parse_boca(html);self.assertEqual(result['source_updated_at'],'2026-08-31');self.assertIsNone(result['source_published_at']);self.assertEqual(result['level'],'第四級：紅色儘速離境')
 def test_boca_rejects_missing_level(self):
  with self.assertRaises(ValueError):a.parse_boca('<table><tr><th>國家地區</th><td>剛果民主共和國</td></tr><tr><th>發布/更新日期</th><td>2026-08-31</td></tr></table>')
 def test_boca_rejects_wrong_congo(self):
  with self.assertRaises(ValueError):a.parse_boca('<table><tr><th>國家地區</th><td>剛果共和國</td></tr></table>')
 def test_singapore_publication_not_footer(self):
  raw='Travel Advisory: Ministry of Health (MOH) Public Health Advisory 25 May 2026 Singaporeans are advised to defer all non-essential travel to the DRC. Copyright last updated on 15 October 2026'
  result=a.parse_sg(raw);self.assertEqual(result['source_published_at'],'2026-05-25');self.assertIsNone(result['source_updated_at'])
 def test_china_publication_not_url_path_date(self):
  raw='提醒中国公民近期谨慎前往刚果（金） 发布时间：2026-05-29 14:17 5月17日，世界卫生组织宣布 22日，世界卫生组织将刚果（金）本国疫情风险等级上调至“极高风险”。非必要不前往'
  result=a.parse_cn(raw);self.assertEqual(result['level'],'极高风险');self.assertEqual(result['source_published_at'],'2026-05-29');self.assertEqual(result['alert_type'],'epidemic-risk');self.assertEqual(result['risk_assessed_at'],'2026-05-22')
 def test_china_requires_explicit_risk(self):
  with self.assertRaises(ValueError):a.parse_cn('提醒中国公民近期谨慎前往刚果（金） 发布时间：2026-05-29 14:17 非必要不前往')
 def test_canada_not_footer_or_menu(self):
  result=a.parse_ca('Last updated: 28 September 2026 13:07 ET DEMOCRATIC REPUBLIC OF THE CONGO - AVOID ALL TRAVEL Date modified: 2025-11-21')
  self.assertEqual(result['source_updated_at'],'2026-09-28')
if __name__=='__main__':unittest.main()
