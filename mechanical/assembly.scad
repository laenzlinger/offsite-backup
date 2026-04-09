// Granit — Mechanical Assembly
// Hammond 1455L2201 enclosure with PCB and 3.5" HDD side-by-side

// All dimensions in mm

// === Hammond 1455L2201 ===
case_length = 220;
case_width  = 103;
case_height = 30.5;
wall_thickness = 1.5;
belly_plate_thickness = 1.0;

// Internal dimensions
int_length = case_length;
int_width  = case_width - 2 * wall_thickness; // ~100mm
int_height = case_height - belly_plate_thickness - wall_thickness; // ~28mm usable

// === 3.5" HDD (standard) ===
hdd_length = 147;
hdd_width  = 101.6;
hdd_height = 26.1;

// === PCB ===
pcb_length = 71;
pcb_width  = 101;
pcb_thickness = 1.6;
standoff_height = 3.0;

// === Layout: side-by-side along case length ===
gap = 2; // gap between PCB and HDD

// Positions (relative to case interior origin)
pcb_x = 0;
pcb_y = (int_width - pcb_width) / 2;
pcb_z = belly_plate_thickness + standoff_height;

hdd_x = pcb_length + gap;
hdd_y = (int_width - hdd_width) / 2;
hdd_z = belly_plate_thickness; // sits flat on belly plate

// === Mounting holes ===
mount_inset = 4; // from PCB edge

// === Colors ===
case_color    = [0.75, 0.75, 0.75, 0.3]; // aluminium, transparent
pcb_color     = [0.0, 0.5, 0.0, 0.9];    // green
hdd_color     = [0.3, 0.3, 0.3, 0.9];    // dark grey
standoff_color = [0.8, 0.7, 0.0, 1.0];   // brass

// === Modules ===

module case_body() {
    color(case_color)
    difference() {
        cube([case_length, case_width, case_height]);
        // Hollow interior
        translate([0, wall_thickness, belly_plate_thickness])
            cube([int_length, int_width, int_height + wall_thickness + 1]);
    }
}

module pcb() {
    color(pcb_color)
    translate([pcb_x, pcb_y, pcb_z])
        cube([pcb_length, pcb_width, pcb_thickness]);
}

module hdd() {
    color(hdd_color)
    translate([hdd_x, hdd_y, hdd_z])
        cube([hdd_length, hdd_width, hdd_height]);
}

module standoff(x, y) {
    color(standoff_color)
    translate([pcb_x + x, pcb_y + y, belly_plate_thickness])
        cylinder(h=standoff_height, d=6, $fn=6);
}

module mounting_holes() {
    standoff(mount_inset, mount_inset);
    standoff(pcb_length - mount_inset, mount_inset);
    standoff(mount_inset, pcb_width - mount_inset);
    standoff(pcb_length - mount_inset, pcb_width - mount_inset);
}

// === Assembly ===

case_body();
pcb();
hdd();
mounting_holes();

// === Info (check clearances) ===
echo(str("PCB top surface: ", pcb_z + pcb_thickness, "mm"));
echo(str("HDD top: ", hdd_z + hdd_height, "mm"));
echo(str("Case interior ceiling: ", belly_plate_thickness + int_height, "mm"));
echo(str("PCB-to-ceiling clearance: ", belly_plate_thickness + int_height - pcb_z - pcb_thickness, "mm"));
echo(str("HDD-to-ceiling clearance: ", belly_plate_thickness + int_height - hdd_z - hdd_height, "mm"));
echo(str("Total occupied length: ", pcb_length + gap + hdd_length, "mm / ", case_length, "mm"));
