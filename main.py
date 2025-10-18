# Main module for Tableau SQL Extractor

from downloader import download_workbook
from extractor import extract_twbx
from parser import parse_twb_for_sql
from saver import save_sql_queries
from config import sign_out_tableau
from typing import List, Dict, Tuple

def process_single_workbook(workbook_id: str, workbook_name: str) -> Dict:
    """
    Process a single workbook through the complete workflow:
    1. Download .twbx workbook using REST API only
    2. Extract .twb XML file
    3. Parse SQL queries
    4. Save queries to individual files
    
    Args:
        workbook_id (str): The ID of the workbook to process
        workbook_name (str): Name for the workbook (used for file naming)
        
    Returns:
        Dict: Result dictionary with success status and details
    """
    result = {
        'workbook_id': workbook_id,
        'workbook_name': workbook_name,
        'success': False,
        'error': None,
        'twbx_path': None,
        'twb_path': None,
        'sql_queries_count': 0,
        'saved_files': []
    }
    
    print(f"\n📋 Processing: {workbook_name} (ID: {workbook_id})")
    print("-" * 40)
    
    try:
        # Step 1: Download the workbook
        print("📥 Step 1: Downloading workbook...")
        twbx_path = download_workbook(workbook_id, workbook_name)
        result['twbx_path'] = twbx_path
        
        # Step 2: Extract the .twb file
        print("📦 Step 2: Extracting .twb file...")
        twb_path = extract_twbx(twbx_path, workbook_name)
        result['twb_path'] = twb_path
        
        # Step 3: Parse SQL queries
        print("🔍 Step 3: Parsing SQL queries...")
        sql_queries = parse_twb_for_sql(twb_path)
        result['sql_queries_count'] = len(sql_queries)
        
        if not sql_queries:
            print("⚠️ No SQL queries found in the workbook")
            result['success'] = True  # Still consider it successful
            return result
        
        # Step 4: Save SQL queries
        print("💾 Step 4: Saving SQL queries...")
        saved_files = save_sql_queries(sql_queries, workbook_name)
        result['saved_files'] = saved_files
        
        # Success summary for this workbook
        print(f"✅ {workbook_name} completed successfully!")
        print(f"   • SQL queries found: {len(sql_queries)}")
        print(f"   • SQL files created: {len(saved_files)}")
        
        result['success'] = True
        return result
            
    except Exception as e:
        error_msg = f"Error processing {workbook_name}: {e}"
        print(f"❌ {error_msg}")
        result['error'] = error_msg
        return result

def main(workbooks: List[Tuple[str, str]]):
    """
    Main function to orchestrate the complete workflow for multiple workbooks:
    1. Download .twbx workbook using REST API only
    2. Extract .twb XML file
    3. Parse SQL queries
    4. Save queries to individual files
    
    Args:
        workbooks (List[Tuple[str, str]]): List of (workbook_id, workbook_name) tuples
    """
    print("🚀 Starting Tableau SQL Extractor (REST API Only)")
    print("=" * 60)
    print(f"📋 Total workbooks to process: {len(workbooks)}")
    print(f"🔒 Using REST API only (VizPortal blocked)")
    print("=" * 60)
    
    # Track overall results
    successful_workbooks = []
    failed_workbooks = []
    total_sql_queries = 0
    total_files_created = 0
    
    try:
        # Process each workbook
        for i, (workbook_id, workbook_name) in enumerate(workbooks, 1):
            print(f"\n🔄 Processing workbook {i}/{len(workbooks)}")
            
            result = process_single_workbook(workbook_id, workbook_name)
            
            if result['success']:
                successful_workbooks.append(result)
                total_sql_queries += result['sql_queries_count']
                total_files_created += len(result['saved_files'])
            else:
                failed_workbooks.append(result)
        
        # Final summary
        print("\n" + "=" * 60)
        print("🎉 BATCH EXTRACTION COMPLETE!")
        print("=" * 60)
        print(f"✅ Successfully processed: {len(successful_workbooks)}/{len(workbooks)} workbooks")
        print(f"❌ Failed: {len(failed_workbooks)} workbooks")
        print(f"📊 Total SQL queries found: {total_sql_queries}")
        print(f"📁 Total SQL files created: {total_files_created}")
        print(f"📁 Output directory: ./sql_output/")
        
        # Show successful workbooks
        if successful_workbooks:
            print(f"\n✅ Successfully processed workbooks:")
            for result in successful_workbooks:
                print(f"   • {result['workbook_name']}: {result['sql_queries_count']} queries, {len(result['saved_files'])} files")
        
        # Show failed workbooks
        if failed_workbooks:
            print(f"\n❌ Failed workbooks:")
            for result in failed_workbooks:
                print(f"   • {result['workbook_name']}: {result['error']}")
            
    except Exception as e:
        print(f"\n❌ Critical error during batch processing: {e}")
        
    finally:
        # Sign out from Tableau Server
        print("\n🚪 Signing out from Tableau Server...")
        sign_out_tableau()
        
if __name__ == "__main__":
    # Example usage - Multiple workbooks
    workbooks_to_process = [
        # ("3ba1e57c-2095-457f-9e62-348c5d169b20","Allocation Productivity Dashboard")

("4d719927-8e53-4adb-82fd-9ad19e59b2ff","AB Test - Video Cataloguing"),
("33337d26-e183-4387-95ab-185b3cc83ca3","Airo AI Calling"),
("992bea59-a2ab-4499-a104-6ad4eb020910","Assisted Dashboard"),
("ba84ec39-7a2e-43d4-83e7-0b64c261d519","Assortment Distribution"),
("c3ab31d4-015f-4d0a-8c82-5950f56c4fa3","ATM (Chatbot + IVR)"),
("6ca9d1b6-1d7a-417a-bba8-6b3072ecb324","Auction Funnel - Tier1"),
("32649792-6595-43de-950f-cc84441b5cc2","Auction-Post Inspection"),
("c757f661-6982-414b-a156-ac250ad58282","Auctions Performance Dashboard"),
("9264066b-97cb-41b0-a059-3a337d249bb7","Audit dashboards"),
("87bc146c-bb9a-48c3-bdf0-121066876ac6","Audit Data - Sales"),
("0d228117-e292-40b2-8275-61ac652fe932","Auto_cj_allocation_proximity Migrated"),
("a36f1995-d9d0-4b7d-90dd-20248d036835","Bajaj Dashboard - Migrated"),
("88a3700b-2536-450e-a026-26112b25b749","Bajaj Ops Funnel Tracking"),
("b5a4982a-0436-4d82-9f37-39255160e449","Banking Sufficiency Dashboard"),
("023d2afe-b475-421a-8fb2-618467e7ad0b","Base_Data_New"),
("5192b836-ce68-4aa0-9f36-c51aa7636a6a","BBNP"),
("cd4499c0-73ab-49b7-9998-a508719f76e3","BC2D_V4 (migrated)"),
("fc18a857-9b35-4c4b-b972-ac1f9da5a553","BC2V Incentive Dashboard 2.0"),
("c33ce102-8286-451b-bbf0-3f54259fbcb4","BC2V Performance 2.0"),
("6491abbf-0052-4dd1-b68c-094bcd3bc4c0","Bengaluru - Brand Dashboard"),
("7a4026d7-5047-4c7e-ad9e-1b1b6af4528f","Bharat RTO - Weekly - REPORT Migrated"),
("17dabe92-2976-44f3-bf92-8b07e5c93057","BI Last Touch Migrated"),
("509d88e7-d44b-4263-8392-60ad29f289cf","BI LT"),
("3d8af5df-a295-4857-ac3f-6b23241b71fb","Blog Dashboard"),
("5e662523-9994-4863-b1fc-9d02678c078b","BOF TAT Dashboard"),
("f104e51c-7c48-48ab-905c-2e52b7aab05a","Bought - Stockin Summary"),
("22923b25-b7a2-46e9-965f-175ccd3ff379","Brand Bidding Dashbaord_"),
("b1565c5d-e4aa-4843-a8bd-89b5aeb2e1b2","Branding Dashboard"),
("85300b3a-085e-46b6-8636-86167fdbb496","Buyer CC Follow-Up Compliance Tracker"),
("d0f8d92d-fce9-4d50-853c-c70c9fcdf787","Buyer CC Leads (First Connect Distribution) 2.0"),
("5b8cfa35-dd25-4c5f-866e-0c89a78feb55","Buyer CC Performance 2.0"),
("504324fc-6182-4884-8a48-d4fe49a55e92","Buyer CC RCA (Internal) 2.0"),
("8d845469-a984-4092-bebd-222f8d3aff8d","Buyer CC Sales Panel Adherence 2.0"),
("8737252d-65a6-4ea0-a59b-20c6ef5e55d5","Buyer CC SLA | Incentive | Sales Panel Adherence 2.0"),
("716d5be6-1c0c-4309-a1a7-bc155cb4acc8","Buyer Classifieds & Partnerships Migrated"),
("23b4fbfe-8bc4-4fd6-91c8-02590b1c87fe","C2B Funnel Dashboard"),
("58122a66-7c09-4aeb-be7c-be37f4c1ceb6","C2B GS Dashboard"),
("7024f6a1-d52a-44a0-926b-378ca6bee769","C2B Manual Funnel"),
("c3077ffa-a286-4a0b-b889-0320b2958960","C2B metrics"),
("597891f8-1904-4b51-8a9d-cfe4d6466c5d","C2B MTD metrics"),
("b52d1a75-b160-4bbd-8532-d1f3775cea0b","C2B Non Funnel GA4 Migrated"),
("17f3d3ce-2a6c-44e3-8cd8-114963e30de2","C2B Overlap & Blog Funnel 2025"),
("64604c3e-cb4c-4778-b043-f7626319a9f3","C2B User Conversion Funnel 2025"),
("484f18c2-e3c0-4440-88ec-d5f881e9f851","C2B Website Funnel 2025"),
("4b5e02ce-5335-4fe3-894d-2473b9d63076","C2B_Affiliate_Master_Tracker_july"),
("9cbfa678-2fcf-4dd1-8b46-4eb4a363cd8f","C2C Agent wise cf performance"),
("6b4d10b7-9b7e-401c-a3aa-8b919f1f4602","C2C Listing Tracker (GA4)"),
("2cbfc256-b294-4b5f-9b56-65e21daca52b","C2C Marketplace"),
("5ab97dc1-9bd1-4fe0-8f25-9a3c4a140c57","C2C P&L"),
("6b88e12a-304f-4249-8b71-28675a36efdc","CC Assisted BCs - Overview"),
("316d44a8-99e9-4ff0-a67b-6a9370003de6","CC Classified Funnel"),
("443073bc-6f00-4a83-a31f-1d10df0c9486","CC LMS A2I Report GA4 2.0"),
("6bb46315-bd35-4e58-b26e-772a70e479c9","CC Performance A|B Analysis 2.0"),
("d47c8ef7-7bed-4b98-b498-d7be17df6455","CC RT"),
("feacfce5-4e83-4447-826e-70dba8d90ff6","CF Intent (Overall View)"),
("c2f27126-e9be-4be4-a3d6-a1b6c90dc9b0","CF-GS Dashboard new (Version-2)"),
("d6df8b10-5ac6-45c2-92bf-1e71260c8ebf","Challan Panel Data"),
("0416e25e-a39e-4b97-a68d-b18764ff643a","Channel Region Wise Inspections VS Assortment Dashboard Migrated"),
("2e7d5fb9-05b0-473c-8967-e5b8fc7b4563","Channel_Reports (Alliances, Affiliates, DSA, CRM) - GA4 Migrated"),
("b3bfb105-b2f7-4de4-9085-053c50a79d50","Chat/Inbound Assisted User Classification"),
("2d4a84a1-20d2-462e-b66b-26de6ef97bb5","CHR Funnel Report"),
("d1d46c57-0155-4b82-b372-0ace8b399892","CJ ATTENDENCE"),
("77f32128-eb94-4f70-b1fa-33a504799cb7","CJ_NPS"),
("19d6bd06-8d88-43dd-a6f2-4b99d0f0ccca","CJ_Performance_Non_Funnel_v2"),
("fb0d6d49-b997-4f99-813f-358f600c752c","CJR Classified Dashboard 2.0"),
("0917fff6-9a2e-4cd1-8fdf-50235bce8010","Classifed Pricing Dashboard"),
("a52f658d-3709-41b3-af66-0ca064dcc5da","Classified Lead to List"),
("0a3c486b-27e5-4dc6-bfc6-90b96921c818","Classified Listings & Revenue"),
("511b09d9-c25b-4285-8111-63c1aa735187","Classified Pricing AB"),
("bc91d782-833b-4c61-988f-03a8d1933d49","Classified Top Funnel"),
("c649cd30-ca8a-468e-8171-a27873714814","Cohort Inventory Days"),
("f24efd10-ca7c-4290-a608-d87510a47f1c","Coming Soon Cars Daily Numbers"),
("3c8e80fb-95e5-4dc7-a20f-88d2e26ced4c","Conversion Dashboard_version4"),
("df9cc2ce-c4d7-49a6-bdfc-11c24d325da5","cost_centre_par_king"),
("280729b7-d497-4c11-954c-d30164c7a4bd","cost_centre_parking"),
("45e8ec12-7213-4c3b-a860-9aedf9daeeb5","Coupon Discount Tracker"),
("5bf0de94-5c97-4073-8156-8f9a0ba0948f","CREDIT-SAARTHI"),
("5fe01cae-c57c-4fb1-b27a-265a98f8c9ae","CRM Dashboard"),
("1c94db7a-1e4f-4274-a0a5-9c1ca5644672","CRM Dashboard (Channelwise Conversion)"),
("4c3ebae0-65e8-47b1-8d04-41af06be2a1f","CRM DASHBOARD OVERALL"),
("652baeef-779e-4bf6-903c-5e611b45e42f","CRM Dashboards"),
("f4174312-9792-44bd-a045-513dc464fbb3","DA Panel Tracker"),
("125bdd19-4ed5-428c-acca-eb178edbbc02","Daily STR (Delivery & Token)"),
("21746c3a-4562-48e6-9d5b-90ab7310837b","Daily STR (Including Delisted Cars)"),
("d952a86c-20c8-46af-9b30-8600067fe91c","Day Wise TD Scheduling (CC)"),
("df64539f-1629-4f10-81c3-1a534d26af26","Dealer Deposit n Refund_new"),
("8ca55417-df25-4eeb-afc3-08506da0e8f3","Dealer Level RCT"),
("bd6c8b0d-33a8-498f-96f3-ca70a4da453a","Dealer Reassigned Viz Dashboard"),
("20868f3c-ca30-4432-b38f-6fd283b33c80","Dealer Retention v2"),
("68560b1d-9eb0-45f4-bd4d-f3b8944ede48","Dealer Tracker"),
("a91ffa45-3beb-41c3-ab97-12d1bc2d61c3","Dealer_Debit_Note_New"),
("1f91ff64-0c5f-4680-ae01-baf87b44621d","Delisted Inventory Summary"),
("fd006b9b-e2b5-4865-9d9f-352fff59172e","Disbursal Dashboard"),
("6c45cfb8-c3eb-402c-91a5-3affc3098147","DIY Live Notif Metrics"),
("5b17912d-bc67-4afa-b627-af5374cdb157","DS Classified Ranking Experiment"),
("ed94944b-2ea5-4297-a456-79c0b0c70b75","DS Search Rank"),
("5b244c0f-cd51-46d5-85b9-2128927622a0","DS Tracker: Personalization"),
("4abb00c9-a62d-4374-acea-d71d7296b04d","DSA_Direct Customers<>CRM"),
("a6dea031-f7bd-43ce-8ece-f7fe089e0c40","ELITE & EDGE_PLUS"),
("54e2ac15-cce1-42d5-ac42-737f8341b6c5","Facebook Marketplace"),
("613839f3-5bb6-4f50-8fdf-badab2e9527d","GMB Review/Rating Dashboard"),
("c70764f2-7a62-499a-a382-b11c81284d9e","Google Reviews (VIC)"),
("47bab08f-d327-4214-8bb3-d37f7a419d85","GS Business ||Schedule BC Calling Matrix"),
("441126c3-71be-417c-831f-77b0cdf3a064","GS Proc : GS: Procurement Rejections Breakup"),
("4fb8a3a7-7113-46dd-bc13-9b14dfbe3aba","Imps/Views/Bids"),
("261e1e35-4922-4044-9c65-4931398ed525","Inspection: TAT"),
("30330fd7-3c9e-4691-ba80-f38ec718e94a","Migrated : DIY Product Funnel Landing Page to Final Offer"),
("458b59b0-fab2-46c9-8e21-1913cc04668e","NEW ATM"),
("62b6e671-d3b8-489f-a5d4-7fd568395134","New Casewise AOP"),
("dcbccc00-8dbb-4a62-85aa-8d1662b86ad3","New GMB"),
("62c3e89b-38da-4eea-8baa-2d18c4f632bd","New_Cars_Overall_Traffic_Migrated"),
("d4098f67-6487-4a64-8601-7a25dd07a59b","On Demand Home Test Drive (CC)"),
("59db849a-f41e-41fd-8a75-e7125a11bd32","Overall_GFD/Overall GFD"),
("afd0c0f3-90b8-41cb-a8db-670aa61f0ac7","Pmaxx - login to delivery funnel"),
("ddab72d2-5990-4ffd-955c-66117b2ab2ab","REVIVE"),
("3abfdd18-6b2d-463d-b1db-30ed16dff6e0","Self Inspection Flag Auction Funnel"),
("b65402d6-6f96-45f6-8395-75353f030b4a","SELL FUNNEL MSITE"),
("5c44ffac-11ae-474e-9a6e-a808ca5fecba","Slot Wise Appointments (CC Seller)"),
("f5159f19-3fe7-424a-83cd-dbe6e81a2cb2","Subscription Bussiness Impact"),
("f5d829d0-6e2f-44e1-8391-bbd12cfec631","Temp (Home page analysis 12Aug- 24 Aug vs 12 Sep - 24 Sep"),
("bcafb025-83d0-45f9-abe6-894857cca177","Test drive NPS"),
("d9c16334-42fe-4153-bc01-c82ce029081c","User Funnel w/t chatbot clicked & initiated v2 - Migrated"),
("d319f8d1-b7ce-4620-8b22-e11366cc73e2","Visit LT"),
("c5d4aa93-0db4-49a7-919f-1c530aa29a00","Workflow TAT"),
("4353059c-c151-4ea6-8085-614e5837506d","CHALLAN PROD ANALYTICS_NEW EVENTS"),
("342f5e72-9707-4b75-95ce-43847380aa0b","Competitor Deep Dive - Sales, Listing & Price"),
("5c8bcc11-2188-49ea-a3c8-46846dd37644","Dealer Dashboard"),
("0a4e8c68-7e5a-4607-b63e-6a17b16bdc23","Default Sorting Experiment (Excluded the T-1 Reserve cars)"),
("1d4e262e-f11c-4059-942d-a84cbe0cb897","Location_Accuracy"),
("9b243ae0-ecc4-4839-807a-2651519fb4d9","Procurement Funnel || Category Core"),
("3e6da73d-4eff-4c7f-9a7c-4be81bda2889","Sourcing Dashboard v3 (migrated_ Mumbai) :True"),
("bc6797df-72f6-462e-9830-5323b74ddf56","UAE - BP/CL & FLP/CL"),
("9d975734-ea8c-4baa-b25f-813a1c187511","UAE - BP/CL FLP/CL"),
("17641125-9729-4c06-8dc0-ed7a660c4a7d","User Funnel w/t chatbot clicked & initiated - Migrated"),
("85c95e9a-d260-4d6a-821b-951916c4faa6","Aadhaar Audience Tracker"),
("9b3fcf00-ebc2-4598-bf82-603467da30dd","BRAND WOW"),
("4a83199f-17f7-408e-bf8a-5cc54222a942","CRM Dashboard - TOF_Migrated"),
("8891fd49-564b-495a-9d46-261f9841dcef","DCF Core Dashboard"),
("91817d93-b75a-413e-a37d-cc610507d002","CSAT Experiment"),
("d3e6d559-0693-4e47-be94-dbc7aa7c262b","Seller Lead Search Engine"),
("03acaf53-e134-4e27-b631-fa159c704136","AB experiments"),
("dcf8face-ffb7-4d9b-bac4-06f499a1e4db","AU VAS Tracker (WIP)"),
("fe7257bc-0a78-4521-bd23-657c0db5264f","Auction- Post Inspection Classified CC Funnel"),
("2ebcfbb7-6537-4772-b8c3-9f58e9e38624","BA Dashboard"),
("49e6eec5-464a-4057-af96-650e4d5d740a","BI2NS Scoring"),
("d1c5ab08-b236-4a07-a731-b01c5f7d2dc6","BI2PH Optimization"),
("f3edc5e4-122c-4739-bd31-86d38b1a8cd0","BO vs TD All Cuts"),
("756e12c4-1469-479a-8a96-450f4992023b","Buyback Initial Funnel"),
("b49cf416-1068-4780-b2a5-c651a59c7ab4","C2B Product Funnel 2025"),
("0c3e2a10-71bd-41f7-9538-46380d8a24a5","C2C E2L Deepdive"),
("0bad35c9-568c-4fb1-8eb5-f30d4640a301","Chat Analysis"),
("e81e9930-fac1-413b-9524-16dc2e0329ec","Chauferly CTAs"),
("5a92245c-5b3e-4a8b-8bcd-7535b3057ba0","CJ Led App Download Adoption"),
("f59bdd27-1ccd-4e7c-8d3b-5e68c094f227","Classified Listing"),
("40cebad2-f282-4880-94f7-4fe591aee80a","Deal Lost & Sold"),
("7caf3a91-90a0-4faf-903d-aa42f63f4c66","Dealer Stats - Elite"),
("e4c24b2b-a45e-41f2-88d8-fcfdbba4cc2a","Deductions"),
("93d1a41e-2922-4aba-8fc9-390a8147ff35","NDL Inpsections"),
("ca87ee50-e9a8-4e76-9aae-eb067fa57b5e","New N1 Updated Dashboard"),
("c62afe3e-55fe-496f-86fb-6adc325ec542","Chatbot- APP and Whatsapp (Migrated)"),
("eeb24d01-a8e2-4dcf-9001-0928d20fccdd","Sales Ops Dependency TAT"),

    ]
    
    # Process all workbooks
    main(workbooks_to_process)
    
    # Alternative: Process single workbook (backward compatibility)
    # main([("d70e9e5a-7621-4a7a-b038-f3a9d145383a", "AUS U2NS benchmarking user cohort")])