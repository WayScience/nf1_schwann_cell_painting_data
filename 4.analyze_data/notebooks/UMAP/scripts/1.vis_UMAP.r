suppressPackageStartupMessages(library(ggplot2)) #plotting
suppressPackageStartupMessages(library(dplyr)) #work with data frames

# Set directory and file structure
umap_dir <- file.path("results")
umap_files <- list.files(umap_dir, pattern = "\\.tsv$", full.names = TRUE)
print(umap_files)

output_fig_dir <- file.path("figures")
umap_prefix <- "UMAP_"
plate_suffix <- "_sc_feature_selected.tsv"
alt_plate_suffix <- "_sc_only_model_features.tsv"

# Define output figure paths as a dictionary where each plate has a figure output path
output_umap_files <- list()
for (umap_file in umap_files) {
    # Extract file name
    file_name <- basename(umap_file)
    
    # Determine plate name based on file suffix
    if (stringr::str_detect(file_name, plate_suffix)) {
        plate <- stringr::str_remove(stringr::str_remove(file_name, umap_prefix), plate_suffix)
    } else if (stringr::str_detect(file_name, alt_plate_suffix)) {
        plate <- stringr::str_remove(stringr::str_remove(file_name, umap_prefix), alt_plate_suffix)
        if (plate == "Plate_6") {
            plate <- "Plate_6_sc_only_model_features"  # Explicit rename for the new file
        }
    } else {
        next  # Skip files that don't match expected patterns
    }

    # Store in dictionary
    output_umap_files[[plate]] <- file.path(output_fig_dir, paste0(umap_prefix, plate))
}

print(output_umap_files)

# Load data
umap_cp_df <- list()
for (plate in names(output_umap_files)) {
    # Find the umap file associated with the plate
    umap_file <- umap_files[stringr::str_detect(umap_files, plate)]
    print(paste("Loading file for plate:", plate, "File path:", umap_file))
    
    # Load in the umap data
    df <- readr::read_tsv(
        umap_file,
        col_types = readr::cols(
            .default = "d",
            "Metadata_Plate" = "c",
            "Metadata_Well" = "c",
            "Metadata_Site" = "c",
            "Metadata_number_of_singlecells" = "d",
            "Metadata_genotype" = "c"
        )
    )

    # Append the data frame to the list
    umap_cp_df[[plate]] <- df 

    # Remove rows with Metadata_Plate == "Plate_3_prime" if plate is Plate_3 (error when loading in the data)
    if (plate == "Plate_3") {
        umap_cp_df[[plate]] <- umap_cp_df[[plate]][umap_cp_df[[plate]]$Metadata_Plate != "Plate_3_prime", ]
    }

    # Remove rows with Metadata_Plate == "Plate_6_filtered" if plate is Plate_6 (error when loading in the data)
    if (plate == "Plate_6") {
        umap_cp_df[[plate]] <- umap_cp_df[[plate]][umap_cp_df[[plate]]$Metadata_Plate != "Plate_6_filtered", ]
    }
}

for (plate in names(umap_cp_df)) {
    # Remove rows with NaNs
    umap_data <- na.omit(umap_cp_df[[plate]])

    # Genotype UMAP file path
    genotype_output_file <- paste0(output_umap_files[[plate]], "_genotype.png")

    # UMAP labeled with genotype
    genotype_gg <- (
        ggplot(umap_data, aes(x = UMAP0, y = UMAP1))
        + geom_point(
            aes(color = Metadata_genotype), size = 1.2, alpha = 0.6
        )
        + theme_bw()
        + scale_color_manual(
            name = "Genotype",
            values = c("Null" = "#BA5A31", "WT" = "#32be73")
        )
    )
    
    ggsave(genotype_output_file, genotype_gg, dpi = 500, height = 6, width = 6)

    # UMAP labeled with cell count
    cell_count_output_file <- paste0(output_umap_files[[plate]], "_cell_count.png")
    
    umap_cell_count_gg <- (
        ggplot(umap_data, aes(x = UMAP0, y = UMAP1))
        + geom_point(
            aes(color = Metadata_number_of_singlecells), size = 1.2, alpha = 0.6
        )
        + theme_bw()
        + theme(
            strip.background = element_rect(colour = "black", fill = "#fdfff4")
        )
        + scale_color_continuous(name = "Number of\nsingle cells\nper well")
    )

    ggsave(cell_count_output_file, umap_cell_count_gg, dpi = 500, height = 6, width = 6)
}

# For only plate 4, look at labelling the constructs to see if there is any clustering
# Load the data frame
platemap_df <- read.csv("../../../0.download_data/metadata/platemap_NF1_plate4.csv")

# Subset the data frame and rename columns
platemap_df <- platemap_df[, c("well_position", "siRNA", "Concentration")]
colnames(platemap_df) <- c("Metadata_Well", "Metadata_siRNA", "Metadata_dose")

# Set the 0 dose to NA to make grey in the plot
platemap_df <- platemap_df %>%
mutate(Metadata_dose = ifelse(Metadata_dose == 0, NA, Metadata_dose))

# Select plate 4 file path from list of umap files
plate_4_path <- umap_files[[6]]

# Load in the umap data for plate 4 only
df <- readr::read_tsv(
    plate_4_path,
    col_types = readr::cols(
        .default = "d",
        "Metadata_Plate" = "c",
        "Metadata_Well" = "c",
        "Metadata_Site" = "c",
        "Metadata_number_of_singlecells" = "c",
        "Metadata_genotype" = "c"
    )
)

# Merge siRNA info onto UMAP df
combined_df <- platemap_df %>% inner_join(df, by = "Metadata_Well")

# siRNA construct UMAP
output_file <- "./figures/UMAP_Plate_4_siRNA_construct.png"

# UMAP faceted by siRNA treatment and labeled with dose
umap_siRNA_construct_gg <- (
    ggplot(combined_df, aes(x = UMAP0, y = UMAP1))
    + geom_point(
            aes(color = Metadata_dose), size = 2, alpha = 0.5
    )
    + theme_bw()
    + scale_color_gradient(
            name = "Dose (nM)",
            low = "#feaaa3", high = "#ee2711",
            na.value = "#727272"
        )
    + facet_wrap(~ Metadata_siRNA, drop = FALSE)
)

ggsave(output_file, umap_siRNA_construct_gg, dpi = 500, height = 6, width = 6)

# Load the platemap data frame for Plate 6
platemap_df <- read.csv("../../../0.download_data/metadata/platemap_NF1_plate6.csv")

# Subset the data frame and rename columns
platemap_df <- platemap_df[, c("well_position", "Institution")]
colnames(platemap_df) <- c("Metadata_Well", "Metadata_Institution")

# Define the two Plate 6 UMAP file paths
plate_6_paths <- umap_files[grepl("UMAP_Plate_6", umap_files)]

# Loop through each of the Plate 6 UMAP files
for (plate_6_path in plate_6_paths) {
    
    # Load in the UMAP data for the current Plate 6 file
    df <- readr::read_tsv(
        plate_6_path,
        col_types = readr::cols(
            .default = "d",
            "Metadata_Plate" = "c",
            "Metadata_Well" = "c",
            "Metadata_Site" = "c",
            "Metadata_number_of_singlecells" = "c",
            "Metadata_genotype" = "c"
        )
    )
    
    # Merge institution info onto UMAP df
    combined_df <- platemap_df %>% inner_join(df, by = "Metadata_Well")
    
    # Define the output file name based on the current Plate 6 file
    output_file <- paste0(
        "./figures/", 
        gsub("Plate_6_sc_feature_selected", "Plate_6", tools::file_path_sans_ext(basename(plate_6_path))),  # Handle the Plate_6_sc_feature_selected condition and remove .tsv
        "_institution.png"
    )

    
    # Create UMAP plot labeled with institution
    umap_institution_gg <- (
        ggplot(combined_df, aes(x = UMAP0, y = UMAP1))
        + geom_point(
                aes(color = Metadata_Institution), size = 1.5, alpha = 0.3
        )
        + theme_bw()
        + scale_color_discrete(name = "Institution")
    )
    
    # Save the plot with a specific output filename
    ggsave(output_file, umap_institution_gg, dpi = 500, height = 6, width = 6)
}

# Select concat plate file path from list of umap files
concat_plate_path <- umap_files[[1]]

# Load in the umap data for plate 4 only
df <- readr::read_tsv(
    concat_plate_path,
    col_types = readr::cols(
        .default = "d",
        "Metadata_Plate" = "c",
        "Metadata_Well" = "c",
        "Metadata_Site" = "c",
        "Metadata_number_of_singlecells" = "c",
        "Metadata_genotype" = "c"
    )
)

# Plate UMAP
output_file <- "./figures/UMAP_concat_model_plate.png"

# UMAP labeled with plate
umap_plate_gg <- (
    ggplot(df, aes(x = UMAP0, y = UMAP1))
    + geom_point(
            aes(color = Metadata_Plate), size = 1.2, alpha = 0.5
    )
    + theme_bw()
    + scale_color_manual(
        name = "Plate",
        values = c("Plate_3" = "#7570b3", "Plate_3_prime" = "#e7298a", "Plate_5" = "#d95f02", "Plate_4" = "#39e729")
    )
)

ggsave(output_file, umap_plate_gg, dpi = 500, height = 6, width = 6)

