suppressPackageStartupMessages(library(ggplot2))
suppressPackageStartupMessages(library(dplyr))


# Set directory and file structure
umap_dir <- file.path("results")
umap_files <- list.files(umap_dir, full.names = TRUE)
print(umap_files)

output_fig_dir <- file.path("figures")
umap_prefix <- "UMAP_"
plate_suffix <- "_sc_feature_selected.tsv"

# Define output figure paths as a dictionary where each plate has a figure output path
output_umap_files <- list()
for (umap_file in umap_files) {
    # Use the file name to extract plate
    plate <- stringr::str_remove(
        stringr::str_remove(
            unlist(
                strsplit(umap_file, "/")
            )[2],
            umap_prefix
        ),
        plate_suffix
    )
    output_umap_files[plate] <- file.path(
        output_fig_dir,
        paste0(umap_prefix, plate)
    )
}
        
print(output_umap_files)


# Load data
umap_cp_df <- list()
for (plate in names(output_umap_files)) {
    # Find the umap file associated with the plate
    umap_file <- umap_files[stringr::str_detect(umap_files, plate)]
    
    # Load in the umap data
    df <- readr::read_tsv(
        umap_file,
        col_types = readr::cols(
            .default = "d",
            "Metadata_Well" = "c",
            "Metadata_Site" = "c",
            "Metadata_number_of_singlecells" = "d",
            "Metadata_genotype" = "c"
        )
    )

    # Append the data frame to the list
    umap_cp_df[[plate]] <- df 
}


for (plate in names(umap_cp_df)) {
    # Genotype UMAP
    output_file <- output_umap_files[[plate]]
    output_file <- paste0(output_file, "_genotype.png")

    genotype_gg <- (
        ggplot(umap_cp_df[[plate]], aes(x = UMAP0, y = UMAP1))
        + geom_point(
            aes(color = Metadata_genotype), size = 0.4, alpha = 0.7
        )
        + theme_bw()
        + scale_color_manual(
            name = "Genotype",
            values = c("Null" = "#BA5A31", "WT" = "#69DC9E", "HET" = "#3c47dd")
        )
    )
    
    ggsave(output_file, genotype_gg, dpi = 500, height = 6, width = 6)

    # Cell Count UMAP
    output_file <- output_umap_files[[plate]]
    output_file <- paste0(output_file, "_cell_count.png")
    
    umap_cell_count_gg <- (
        ggplot(umap_cp_df[[plate]], aes(x = UMAP0, y = UMAP1))
        + geom_point(
            aes(color = Metadata_number_of_singlecells), size = 0.4, alpha = 0.7
        )
        + theme_bw()
        + theme(
            strip.background = element_rect(colour = "black", fill = "#fdfff4")
        )
        + scale_color_continuous(name = "Number of\nsingle cells\nper well")
    )

    ggsave(output_file, umap_cell_count_gg, dpi = 500, height = 6, width = 6)

}


# For only plate 4, look at labelling the constructs to see if there is any clustering
# Load the data frame
platemap_df <- read.csv("../../../0.download_data/metadata/platemap_NF1_plate4.csv")

# Subset the data frame and rename columns
platemap_df <- platemap_df[, c("well_position", "siRNA", "Concentration")]
colnames(platemap_df) <- c("Metadata_Well", "Metadata_siRNA", "Metadata_dose")

plate_4_path <- umap_files[[5]]

# Load in the umap data for plate 4 only
df <- readr::read_tsv(
    plate_4_path,
    col_types = readr::cols(
        .default = "d",
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

umap_siRNA_construct_gg <- (
    ggplot(combined_df, aes(x = UMAP0, y = UMAP1))
    + geom_point(
            aes(shape = Metadata_siRNA, color = Metadata_dose), size = 2, alpha = 0.5
    )
    + scale_shape_discrete(name = "siRNA Treatments")
    + theme_bw()
    + scale_color_gradient(
            name = "Dose",
            low = "#FFA500", high = "#004b00"
        )
)

ggsave(output_file, umap_siRNA_construct_gg, dpi = 500, height = 6, width = 6)


