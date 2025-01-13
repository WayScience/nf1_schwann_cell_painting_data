suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(ggplot2))
suppressPackageStartupMessages(library(platetools))

platemap_files <- list.files(pattern = "^platemap_NF1*", full.names = TRUE)
print(platemap_files)

output_fig_dir <- file.path("platemap_figures")
platemap_suffix <- "_platemap_figure.png"

output_platemap_files <- list()
for (platemap_file in platemap_files) {
    # Extract plate name and remove suffix 
    plate <- basename(platemap_file)
    plate <- stringr::str_remove(plate, "_platemap.csv")
    plate <- stringr::str_extract(plate, "(?<=platemap_NF1_).*")  # Extracts the plate name
    plate <- stringr::str_remove(plate, "\\.csv$")  # Remove the .csv extension

    output_platemap_files[[plate]] <- file.path(output_fig_dir, paste0(plate, platemap_suffix))
}

print(output_platemap_files)


# Load in all platemap CSV files
platemap_dfs <- list()
for (plate in names(output_platemap_files)) {
    # Find the umap file associated with the plate
    platemap_file <- platemap_files[stringr::str_detect(platemap_files, plate)]
    
    # Load in the umap data
    df <- readr::read_csv(
    platemap_file,
    col_types = readr::cols(.default = "c")
)

    platemap_dfs[[plate]] <- df 
}

print(platemap_dfs)

for (plate in names(platemap_dfs)) {
    if (plate %in% c("plate1", "plate2")) {
    # Get the updated plate name
    updated_plate <- paste0("Plate ", as.numeric(gsub("plate", "", plate)))

    # output for each plate
    output_file <- output_platemap_files[[plate]]
    output_file <- paste0(output_file)
    
    platemap <-
        platetools::raw_map(
            data = platemap_dfs[[plate]]$genotype,
            well = platemap_dfs[[plate]]$well_position,
            plate = 96,
            size = 8
        ) +
        ggtitle(paste("Platemap layout for", updated_plate)) +
        theme(plot.title = element_text(size = 10, face = "bold")) +
        ggplot2::scale_fill_discrete(name = "Genotype") 

    ggsave(
        output_file,
        platemap,
        dpi = 500,
        height = 3.5,
        width = 6
    )
    }
}

for (plate in names(platemap_dfs)) {
    if (plate %in% c("plate3")) {
    # Get the updated plate name
    updated_plate <- paste0("Plate ", as.numeric(gsub("plate", "", plate)))

    # output for each plate
    output_file <- output_platemap_files[[plate]]
    output_file <- paste0(output_file)
    
    platemap <-
        platetools::raw_map(
            data = as.numeric(platemap_dfs[[plate]]$seed_density),
            well = platemap_dfs[[plate]]$well_position,
            plate = 96,
            size = 8
        ) +
        ggtitle(paste("Platemap layout for", updated_plate)) +
        theme(plot.title = element_text(size = 10, face = "bold")) +
        ggplot2::geom_point(aes(shape = platemap_dfs[[plate]]$genotype)) +
        ggplot2::scale_shape_discrete(name = "Genotype") +
        ggplot2::scale_fill_gradient2(
        name = "Seed Density",
        low = "white",
        high = "red",
        )  

    ggsave(
        output_file,
        platemap,
        dpi = 500,
        height = 3.5,
        width = 6
    )
    }
}

for (plate in names(platemap_dfs)) {
    if (plate %in% c("plate4")) {
    # Get the updated plate name
    updated_plate <- paste0("Plate ", as.numeric(gsub("plate", "", plate)))

    # Remove .png extension and add new suffixes
    filename_without_ext <- tools::file_path_sans_ext(output_platemap_files[[plate]])
    output_file_genotype <- paste0(filename_without_ext, "_genotype.png")
    output_file_dose <- paste0(filename_without_ext, "_dose.png")

    # Platemap for genotype
    platemap_genotype <- platetools::raw_map(
        data = platemap_dfs[[plate]]$genotype,
        well = platemap_dfs[[plate]]$well_position,
        plate = 96,
        size = 8
    ) +
    ggtitle(paste("Genotype platemap layout for", updated_plate)) +
    theme(plot.title = element_text(size = 10, face = "bold")) +
    ggplot2::scale_fill_discrete(name = "Genotype")
    
    # Platemap for dose
    platemap_dose <- platetools::raw_map(
        data = as.character(platemap_dfs[[plate]]$Concentration),
        well = platemap_dfs[[plate]]$well_position,
        plate = 96,
        size = 8
    ) +
    ggtitle(paste("siRNA treatment and dose platemap layout for", updated_plate)) +
    theme(plot.title = element_text(size = 10, face = "bold")) +
    ggplot2::geom_point(aes(shape = platemap_dfs[[plate]]$siRNA)) +
    ggplot2::scale_shape_discrete(name = "siRNA Treatments", limits = c("None", "Scramble", "NF1 Target 1", "NF1 Target 2")) +
    ggplot2::scale_fill_manual(
        name = "Concentrations (nM)",
        values = c("#eff6ef", "#b7deb7", "#56bc56", "#018301", "#015201", "#003800"),
        guide = guide_legend(override.aes = list(size = 5)),
    ) +
    theme(
        legend.text = element_text(size = 5),
        legend.title = element_text(size = 6),
        legend.position = "right",
        # move legend around so it fits better on the screen
        legend.margin = margin(-10, 0, 10, 0)
    )

    # Saving the platemaps
    ggsave(
        output_file_genotype,
        platemap_genotype,
        dpi = 500,
        height = 3.5,
        width = 6
    )
    
    ggsave(
        output_file_dose,
        platemap_dose,
        dpi = 500,
        height = 3.5,
        width = 6
    )
    }
}

for (plate in names(platemap_dfs)) {
    if (plate %in% c("plate5")) {
    # Get the updated plate name
    updated_plate <- paste0("Plate ", as.numeric(gsub("plate", "", plate)))

    # output for each plate
    output_file <- output_platemap_files[[plate]]
    output_file <- paste0(output_file)
    
    platemap <-
        platetools::raw_map(
            data = platemap_dfs[[plate]]$genotype,
            well = platemap_dfs[[plate]]$well_position,
            plate = 96,
            size = 8
        ) +
        ggtitle(paste("Platemap layout for", updated_plate)) +
        theme(plot.title = element_text(size = 10, face = "bold")) +
        ggplot2::scale_fill_discrete(name = "Genotype")  

    ggsave(
        output_file,
        platemap,
        dpi = 500,
        height = 3.5,
        width = 6
    )
    }
}

for (plate in names(platemap_dfs)) {
    if (plate == "plate6") {
        # Get the updated plate name
        updated_plate <- paste0("Plate ", as.numeric(gsub("plate", "", plate)))

        # Output for the plate
        output_file <- output_platemap_files[[plate]]
        output_file <- paste0(output_file)
        
        platemap <-
            platetools::raw_map(
                data = platemap_dfs[[plate]]$genotype,
                well = platemap_dfs[[plate]]$well_position,
                plate = 96,
                size = 8
            ) +
            ggtitle(paste("Platemap layout for", updated_plate)) +
            theme(plot.title = element_text(size = 10, face = "bold")) +
            ggplot2::scale_fill_discrete(name = "Genotype") +
            ggplot2::geom_point(aes(shape = platemap_dfs[[plate]]$Institution)) +
            ggplot2::scale_shape_discrete(name = "Institution\n(cell line)")

        ggsave(
            output_file,
            platemap,
            dpi = 500,
            height = 3.5,
            width = 6
        )
    }
}
