library(stats)
library(ggplot2)
library(grid)
library(gridExtra)


# Parameters
ptero_filename = "ptero_data.tsv"
galaxy_filename = "galaxy_data.tsv"

colors <- c("ptero"="#AF5784", "galaxy"="#527614")
major_grid_color = "grey"
major_grid_size = 0.4
minor_grid_color = "grey"
minor_grid_size = 0.1

data_line_size = 1
data_point_size = 3

# Functions
load_data <- function(filename, label, sleep=0.1, workers=4) {
    data <- read.delim(filename, header=F)
    data$label <- label
    data$overhead <- data$V2 - (data$V1 * sleep / workers)
    data
}

f_test <- function(data) {
    lin <- lm(V2~V1, data)
    quad <- lm(V2~poly(V1, 2, raw=TRUE), data)
    var.test(lin, quad)
}

plot_throughput <- function(data, xmin=0, xmax=2000, sleep=0.1, workers=4) {
    data$throughput_percent <- 100 * (data$V1 / data$V2) / (workers / sleep)
    p <- ggplot(data, aes(x=V1, y=throughput_percent, group=label, color=label))
    p <- p + geom_point(size=data_point_size)
    p <- p + geom_smooth(se=FALSE, size=data_line_size)
    p <- p + theme(
        legend.position="none",

        axis.ticks.y=element_blank(),

        panel.grid.major.x=element_blank(),
        panel.grid.minor.x=element_blank(),

        panel.grid.major.y=element_line(color=major_grid_color,
                                        size=major_grid_size),
        panel.grid.minor.y=element_line(color=minor_grid_color,
                                        size=minor_grid_size),

        panel.background=element_blank(),
        plot.background=element_blank()
    )
    p <- p + scale_x_continuous(limits=c(xmin, xmax))
    p <- p + scale_y_log10(
        limits=c(0.4, 100),
        breaks=c(0.1, 1, 10, 100),
        labels=c('0.1', '1', '10', '100'),
        minor_breaks=log10(c(
            0.1 * seq(2, 8, by=2),
              1 * seq(2, 8, by=2),
             10 * seq(2, 8, by=2),
            100 * seq(2, 8, by=2)
        ))
    )
    p <- p + scale_color_manual(values=colors)
    p <- p + xlab("Number of Parallel Operations")
    p <- p + ylab("Operation Throughput [% of Theoretical]")
    p
}

plot_total_runtime <- function(ptero_data, galaxy_data, xmin=0, xmax=20000,
                               sleep=0.1, workers=4) {
    smooth_x <- seq(min(1), max(ptero_data$V1), 10)
    theoretical_data <- data.frame(V1=smooth_x, V2=0.1*smooth_x/4, label="theoretical")

    ptero_lin <- lm(V2~V1, ptero_data)
    ptero_quad <- lm(V2~poly(V1, 2, raw=TRUE), ptero_data)
    ptero_smooth = data.frame(V1=smooth_x,
                              V2=ptero_lin$coefficients[1] + smooth_x * ptero_lin$coefficients[2],
                              label="ptero")

    galaxy_lin <- lm(V2~V1, galaxy_data)
    galaxy_quad <- lm(V2~poly(V1, 2, raw=TRUE), galaxy_data)
    galaxy_smooth = data.frame(V1=smooth_x,
                               V2=galaxy_quad$coefficients[1] + smooth_x * galaxy_quad$coefficients[2] + (smooth_x ^ 2) * galaxy_quad$coefficients[3],
                               label="galaxy")

    combined_smooth <- rbind(ptero_smooth, galaxy_smooth)


    p <- ggplot(rbind(ptero_data, galaxy_data), aes(x=V1, y=V2, group=label,
                                                    color=label))
    p <- p + geom_point(size=data_point_size)
    p <- p + geom_line(data=combined_smooth, size=data_line_size)
    p <- p + geom_line(data=theoretical_data, color="black", size=data_line_size)
    p <- p + theme(
        legend.position="none",

        axis.ticks.y=element_blank(),

        panel.grid.major.x=element_blank(),
        panel.grid.minor.x=element_blank(),

        panel.grid.major.y=element_line(color=major_grid_color,
                                        size=major_grid_size),
        panel.grid.minor.y=element_line(color=minor_grid_color,
                                        size=minor_grid_size),

        panel.background=element_blank(),
        plot.background=element_blank()
    )
    p <- p + scale_x_continuous(limits=c(xmin, xmax))
    p <- p + scale_y_log10(
        limits=c(1, max(galaxy_data$V2)),
        breaks=c(1, 10, 100, 1000, 10000),
        minor_breaks=log10(c(
               1 * seq(2, 8, by=2),
              10 * seq(2, 8, by=2),
             100 * seq(2, 8, by=2),
            1000 * seq(2, 8, by=2)
        ))
    )
    p <- p + scale_color_manual(values=colors)
    p <- p + xlab("Number of Parallel Operations")
    p <- p + ylab("Total Run Time [seconds]")
    p
}


plot_overhead_lin <- function(ptero_data, galaxy_data, xmin=0, xmax=5000) {
    smooth_x <- seq(min(1), max(ptero_data$V1), 10)

    ptero_lin <- lm(overhead~V1, ptero_data)
    ptero_smooth = data.frame(V1=smooth_x,
                              overhead=ptero_lin$coefficients[1] + smooth_x * ptero_lin$coefficients[2],
                              label="ptero")

    galaxy_quad <- lm(overhead~poly(V1, 2, raw=TRUE), galaxy_data)
    galaxy_smooth = data.frame(V1=smooth_x,
                               overhead=galaxy_quad$coefficients[1] + smooth_x * galaxy_quad$coefficients[2] + (smooth_x ^ 2) * galaxy_quad$coefficients[3],
                               label="galaxy")

    combined_smooth <- rbind(ptero_smooth, galaxy_smooth)


    p <- ggplot(rbind(ptero_data, galaxy_data), aes(x=V1, y=overhead,
                                                    group=label, color=label))
    p <- p + geom_point(size=data_point_size)
    p <- p + geom_line(data=combined_smooth, size=data_line_size)
    p <- p + theme(
        legend.position="none",

        axis.ticks.y=element_blank(),

        panel.grid.major=element_blank(),
        panel.grid.minor=element_blank(),

        panel.background=element_blank(),
        plot.background=element_blank()
    )
    p <- p + scale_x_continuous(limits=c(0, xmax))
    p <- p + scale_y_continuous(limits=c(0, 3e4))

    p <- p + scale_color_manual(values=colors)
    p <- p + xlab("Number of Parallel Operations")
    p <- p + ylab("Total Overhead [seconds]")
    p
}

plot_overhead_log <- function(ptero_data, galaxy_data, xmin=10, xmax=20000) {
    smooth_x <- seq(min(1), max(ptero_data$V1), 10)
    theoretical_data <- data.frame(V1=smooth_x, V2=0.1*smooth_x/4, label="theoretical")

    ptero_lin <- lm(overhead~V1, ptero_data)
    ptero_smooth = data.frame(V1=smooth_x,
                              overhead=ptero_lin$coefficients[1] + smooth_x * ptero_lin$coefficients[2],
                              label="ptero")

    galaxy_quad <- lm(overhead~poly(V1, 2, raw=TRUE), galaxy_data)
    galaxy_smooth = data.frame(V1=smooth_x,
                               overhead=galaxy_quad$coefficients[1] + smooth_x * galaxy_quad$coefficients[2] + (smooth_x ^ 2) * galaxy_quad$coefficients[3],
                               label="galaxy")

    combined_smooth <- rbind(ptero_smooth, galaxy_smooth)

    p <- ggplot(rbind(ptero_data, galaxy_data), aes(x=V1, y=overhead,
                                                    group=label, color=label))
    p <- p + geom_point(size=data_point_size)
    p <- p + geom_line(data=combined_smooth, size=data_line_size)
    p <- p + theme(
        legend.position="none",

        axis.ticks.y=element_blank(),

        panel.grid.major=element_blank(),
        panel.grid.minor=element_blank(),

        panel.background=element_blank(),
        plot.background=element_blank()
    )

    p <- p + scale_x_log10(
        limits=c(xmin, xmax),
        breaks=c(20, 200, 2000, 20000)
    )
    p <- p + scale_y_log10(limits=c(1, 1e5))
#        limits=c(1, max(galaxy_data$V2)),
#        breaks=c(1, 10, 100, 1000, 10000),
#        minor_breaks=log10(c(
#               1 * seq(2, 8, by=2),
#              10 * seq(2, 8, by=2),
#             100 * seq(2, 8, by=2),
#            1000 * seq(2, 8, by=2)
#        ))
#    )

    p <- p + scale_color_manual(values=colors)
    p <- p + xlab("Number of Parallel Operations")
    p <- p + ylab("Total Overhead [seconds]")
    p
}



# Script
ptero_data <- load_data(ptero_filename, "ptero")
galaxy_data <- load_data(galaxy_filename, "galaxy")

combined_data <- rbind(ptero_data, galaxy_data)


ptero_f_test <- f_test(ptero_data)
galaxy_f_test <- f_test(galaxy_data)
print(sprintf("PTero F test p-value: %0.02e", ptero_f_test$p.value))
print(sprintf("Galaxy F test p-value: %0.02e", galaxy_f_test$p.value))


#runtime <- plot_total_runtime(ptero_data, galaxy_data)
#throughput <- plot_throughput(combined_data)

overhead_lin <- plot_overhead_lin(ptero_data, galaxy_data)
overhead_log <- plot_overhead_log(ptero_data, galaxy_data)

pdf("ptero-overhead-lin.pdf")
print(overhead_lin)
dev.off()

pdf("ptero-overhead-log.pdf")
print(overhead_log)
dev.off()

grid.arrange(#runtime, throughput,
             overhead_lin, overhead_log,
             ncol=2)
