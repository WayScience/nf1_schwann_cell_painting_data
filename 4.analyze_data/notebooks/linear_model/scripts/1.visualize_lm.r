suppressPackageStartupMessages(library(ggplot2))
suppressPackageStartupMessages(library(dplyr))


# path to tsv with LM coefficients
lm_results_dir <- file.path("./results")
lm_file <- file.path(lm_results_dir, "./linear_model_cp_features_plate1.tsv")

# save path for figure
lm_fig_dir <- file.path("./figures")
lm_fig <- file.path(lm_fig_dir, "linear_model_cp_features_plate1.png")

# Load and process linear model data
lm_df <- readr::read_tsv(
    lm_file,
    col_types = readr::cols(.default = "d", feature = "c")
)

print(dim(lm_df))
head(lm_df)


# Arrange by absolute value coefficient
# Split out components of feature name for visualization
lm_df <- lm_df %>%
    dplyr::arrange(desc(abs(Null_coef))) %>%
    tidyr::separate(
        feature,
        into = c(
            "compartment",
            "feature_group",
            "measurement",
            "channel",
            "parameter1",
            "parameter2"
        ),
        sep = "_",
        remove = FALSE
    ) %>%
    dplyr::mutate(channel_cleaned = channel)

# Clean channel for visualization and interpretation
lm_df$channel_cleaned <-
    dplyr::recode(
        lm_df$channel_cleaned,
        "DAPI" = "nuclei",
        "GFP" = "ER",
        "RFP" = "actin",
        .default = "other",
        .missing = "other"
    )

# Print to make sure that the above clean up worked
print(dim(lm_df))
head(lm_df, 10)


# Specify order so that the organelles match the correct color (red, green, blue)
color_order <- c("actin", "ER", "nuclei", "other")

# Plot the linear model coefficients for the WT genotype contribution
# Positive coeff = more likely to be WT cell if feature increases
# Negative coeff = more likely to be Null cell if feature increases
lm_fig_gg <- (
    ggplot(lm_df, aes(x = cell_count_coef, y = WT_coef))
    +
        geom_point(aes(size = r2_score, color = factor(channel_cleaned, levels = color_order)), alpha = 0.7)
        +
        geom_vline(xintercept = 0, linetype = "dashed", color = "red")
        +
        geom_density2d(color = "black", show.legend = FALSE)
        +
        theme_bw()
        +
        guides(
            color = guide_legend(title = "Channel\n(if applicable)", order = 1),
            size = guide_legend(title = "R2 score")
        )
        +
        ylab("WT genotype contribution (LM beta coefficient)")
        +
        xlab("Cell count contribution (LM beta coefficient)")
        +
        ggtitle("Scatter plot of linear model coefficients per CellProfiler feature\n for Plate 1") # nolint
)

# Output figure
ggsave(lm_fig, lm_fig_gg, dpi = 500, height = 6, width = 6)

# Show figure
lm_fig_gg

