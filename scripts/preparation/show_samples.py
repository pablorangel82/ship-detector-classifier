from ultralytics.data.utils import visualize_image_annotations

def show ():
    label_map = {
        0: "Container Ships",
        1: "Bulk Carriers",
        2: "Passenger Ships",
        3: "Ro-ro Passenger Ships",
        4: "Ro-ro Cargo Ships",
        5: "Tugs",
        6: "Vehicles Carriers",
        7: "Reefers",
        8: "Yachts",
        9: "Sailing Vessels",
        10:"Heavy Load Carriers",
        11:"Wood Chips Carriers",
        12:"Livestock Carriers",
        13:"Fire Fighting Vessels",
        14:"Patrol Vessels",
        15:"Platforms",
        16:"Standby Safety Vessels",
        17:"Combat Vessels",
        18:"Training Ships",
        19:"Icebreakers",
        20:"Replenishment Vessels",
        21:"Tankers",
        22:"Fishing Vessels",
        23:"Supply Vessels",
        24:"Carrier Floating",
        25:"Dredgers"
    }


    # Visualize
    output_img_path = r"D:\dataset\first_schema_aug\train\images\14962.jpg" 
    output_label_path = r"D:\dataset\first_schema_aug\train\labels\14962.txt" 

    visualize_image_annotations(
        output_img_path,
        output_label_path,
        label_map,
    )