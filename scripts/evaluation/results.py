import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
import os
from matplotlib.patches import Ellipse
from scipy.stats import t
from scipy.stats import chi2
import codecs

class SaveResults:

    @staticmethod
    def calculate_pearson_correlation(distance_data,
            position_error,
            speed_error,
            course_error,
            output_path):

        distance = np.array(distance_data)
        pos = np.abs(np.array(position_error))
        speed = np.abs(np.array(speed_error))
        course = np.abs(np.array(course_error))

        r_pos, p_pos = pearsonr(distance, pos)
        r_speed, p_speed = pearsonr(distance, speed)
        r_course, p_course = pearsonr(distance, course)

        print("\n================ Pearson Correlation ================")
        print(f"Distance vs Position Error : r={r_pos:.3f}  p={p_pos:.3e}")
        print(f"Distance vs Speed Error    : r={r_speed:.3f}  p={p_speed:.3e}")
        print(f"Distance vs Course Error   : r={r_course:.3f}  p={p_course:.3e}")
        print("=====================================================\n")

        SaveResults.plot_person_analisys(distance, pos,
                       "Distance (m)",
                       "Position Error (m)",
                       output_path,
                       f"test_pearson_position.png")

        SaveResults.plot_person_analisys(distance, speed,
                      "Distance (m)",
                      "Speed Error (knots)",
                      output_path,
                      f"test_pearson_speed.png")

        SaveResults.plot_person_analisys(distance, course,
                      "Distance (m)",
                      "Course Error (deg)",
                      output_path,
                      f"test_pearson_course.png")

    @staticmethod
    def plot_person_analisys(x, y, xlabel, ylabel, path, filename):

        x = np.array(x)
        y = np.array(y)

        plt.figure(figsize=(7,3))

        plt.scatter(x, y, s=15, alpha=0.5)

        m, b = np.polyfit(x, y, 1)
        plt.plot(x, m*x + b, linewidth=2)

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(True)

        plt.tight_layout()

        full_path = os.path.join(path, filename)
        plt.savefig(full_path, dpi=600)

        plt.close()

    @staticmethod
    def plot_trajectory_comparison(data, path, test_case):
        fig, ax = plt.subplots(figsize=(8,4))
        windows = []
        x_gt, y_gt = [], []
        x_track, y_track = [], []
        ellipses = []
        distance_errors = []
        mx_list, my_list = [], []

        n = len(data)

        for i, d in enumerate(data):
            window, x_path_gt, y_path_gt, x_path_track, y_path_track, mx, my, distance_error, width, height, angle = d
            windows.append(window)
            x_gt.append(x_path_gt)
            y_gt.append(y_path_gt)
            x_track.append(x_path_track)
            y_track.append(y_path_track)
            mx_list.append(mx)
            my_list.append(my)
            distance_errors.append(distance_error)

        norm = plt.Normalize(min(windows), max(windows))
        cmap = plt.cm.viridis

        line_color_gt = '#08519c'     
        line_color_track = '#a50f15'  

        ax.plot(x_gt, y_gt, color=line_color_gt, label='Ground Truth', linewidth=2)
        ax.plot(x_track, y_track, color=line_color_track, label='Track', linewidth=2)

        for i in range(n):
            color = cmap(norm(windows[i]))

            ax.plot(x_gt[i], y_gt[i],
                    marker='o', markersize=10,
                    markerfacecolor=color,
                    markeredgecolor='black',
                    markeredgewidth=0.7,
                    linestyle='None')

            ax.plot(x_track[i], y_track[i],
                    marker='o', markersize=10,
                    markerfacecolor=color,
                    markeredgecolor='black',
                    markeredgewidth=0.7,
                    linestyle='None')

            ellipse_track = Ellipse(
                (x_track[i], y_track[i]),
                data[i][8], data[i][9],  
                angle=data[i][10],
                facecolor=color,
                edgecolor='black',
                alpha=0.3,
                linewidth=1
            )
            ax.add_patch(ellipse_track)

        for (x1, y1, x2, y2) in zip(x_gt, y_gt, x_track, y_track):
            ax.plot([x1, x2], [y1, y2], color='gray', linewidth=0.5, alpha=1)

        for window, distance_error, mx, my in zip(windows, distance_errors, mx_list, my_list):
            ax.text(mx, my, f'{distance_error:.0f}m', fontsize=10, color='black')

        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, pad=0.02)
        cbar.set_label('Time Window (s)')

        ax.set_xlabel('X Position (m)')
        ax.set_ylabel('Y Position (m)')
        ax.set_title('Trajectory (χ² = 95%)\nColor indicates time progression')

        ax.legend()

        ax.grid(False)
        ax.set_axis_off()

        path_to_save = os.path.join(path, 'results', f'test_{test_case}_trajectory_comparison.png')   
        plt.savefig(path_to_save, dpi=600, bbox_inches='tight')
        plt.close()

    @staticmethod
    def plot_rmse(context, dimension, unit, windows, rmse_graph_0, rmse_graph_5, rmse_graph_10, rmse_graph_20, path, test_case):
        colors = {
                    '0': '#1b9e77',
                    '5': '#d95f02',
                    '10': '#7570b3',
                    '20': '#e7298a'
                }
        fig, axes = plt.subplots(1,1,figsize=(8,4), sharex=True)
        plt.plot(windows, rmse_graph_0, color=colors['0'], marker='o',linewidth=2)
        plt.plot(windows, rmse_graph_5, color=colors['5'], marker='o',linewidth=2)
        plt.plot(windows, rmse_graph_10, color=colors['10'], marker='o',linewidth=2)
        plt.plot(windows, rmse_graph_20, color=colors['20'], marker='o',linewidth=2)
        axes.set_xlabel("Window (seconds)")
        axes.set_ylabel(f'{context} error in {dimension} ({unit})')
        labels = [f'0% discarded', f'5% discarded', f'10% discarded', f'20% discarded']
        axes.set_title(f"RMSE {dimension} with different Percentiles Discarded")
        axes.legend(labels)
        plt.tight_layout()
        path_to_save = os.path.join(path,'results/',f'test_{test_case}_rmse_{context}_{dimension}.png')   
        plt.savefig(path_to_save, dpi=600, bbox_inches='tight') 

    @staticmethod
    def plot_boxplots(temporal, metrics, grouped_rmse, output_folder):
        os.makedirs(output_folder, exist_ok=True)
        fig, axes = plt.subplots(1, 3, figsize=(8,4))
        for ax, (metric, (title_name, unit)) in zip(axes, metrics.items()):
            data = []
            labels = []
            for discard in sorted(grouped_rmse.keys()):
                try:
                    values = np.array(grouped_rmse[discard][metric][0])
                except:
                    continue
                global_rmse = np.mean(values, axis=1)
                data.append(global_rmse)
                labels.append(f'{discard}%')
            ax.boxplot(data, labels=labels, showmeans=True)
            ax.set_title(title_name)
            ax.set_xlabel('Discard (%)')
            ax.set_ylabel(f'{temporal} RMSE ({unit})')
            ax.grid(True)
        fig.suptitle('RMSE by Discard Percentage')
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, f'{temporal}_rmse_boxplots.png'), dpi=600)
        plt.close()

    @staticmethod
    def compute_statistics(values, use_confidence_interval=True):
        values = np.array(values)
        mean = np.mean(values, axis=0)
        std = np.std(values, axis=0, ddof=1)
        n = values.shape[0]
        if use_confidence_interval and n > 1:
            t_value = t.ppf(0.975, df=n-1)
            margin = t_value * std / np.sqrt(n)
        else:
            margin = std
        return mean, margin

    @staticmethod
    def plot_mean(temporal, metrics, grouped_rmse, windows_ref, output_folder):
        fig, axes = plt.subplots(1, 3, figsize=(7,3), sharex=True)
        for ax, (metric, (title, unit)) in zip(axes, metrics.items()):
            for discard in sorted(grouped_rmse.keys()):
                try:
                    mean, margin = SaveResults.compute_statistics(
                        grouped_rmse[discard][metric][0]
                    )
                except:
                    continue
                lower = mean - margin
                upper = mean + margin
                ax.plot(
                    windows_ref,
                    mean,
                    linewidth=2,
                    label=f'{discard}%'
                )
                ax.fill_between(
                    windows_ref,
                    lower,
                    upper,
                    alpha=0.15
                )
            ax.set_title(title)
            ax.set_xlabel('Window (seconds)')
            ax.set_ylabel(f'{temporal} RMSE ({unit})')
            ax.grid(True)
        handles, labels = axes[0].get_legend_handles_labels()
        fig.legend(
            handles,
            labels,
            loc='upper right',
            ncol=len(grouped_rmse)
        )
        fig.suptitle('RMSE Distribution by Discard Percentage')
        plt.tight_layout()
        plt.savefig(
            os.path.join(output_folder, f'{temporal}_rmse_mean.png'),
            dpi=600
        )
        plt.close()

    @staticmethod
    def plot_nees(all_nees):
        print(all)
        n = 4
        alpha = 0.05
        N = len(all_nees)
        lower = chi2.ppf(alpha/2, n)
        upper = chi2.ppf(1-alpha/2, n)
        nees_mean = np.mean(all_nees)
        nees_std = np.std(all_nees)

        print(nees_mean,nees_std, lower, upper)
        # plt.figure(figsize=(8, 4))
        # plt.plot(windows,all_nees, label="NEES")
        # plt.axhline(n, linestyle="--", label=f"Expected NEES:{n}")
        # plt.axhline(lower, color="red", linestyle=":", label=f"Lower bound (95%):{lower:.2f}")
        # plt.axhline(upper, color="red", linestyle=":", label=f"Upper bound (95%):{upper:.2f}")
        # plt.xlabel("Window (s)")
        # plt.ylabel("NEES")
        # plt.suptitle('Average NEES per Window')
        # plt.legend()
        # plt.savefig(os.path.join(output_folder, 'nees.png'), dpi=600)

    @staticmethod
    def plot_errors_by_discard(temporal, metrics, plot_data, output_folder):
        plt.rcParams.update({
                'font.family': 'serif',     
                'font.size': 8,              
                'axes.titlesize': 8,
                'axes.labelsize': 8,
                'legend.fontsize': 5,
                'xtick.labelsize': 6,
                'ytick.labelsize': 6
            })
        os.makedirs(output_folder, exist_ok=True)
        names = [
            'INGÁ II',
            'NEVES V',
            'OCEAN EUPHROSYNE',
            'LOG IN PATANAL',
            'GEOMAR',
            'TS MARRENTO'
        ]
        for discard_percent, data in plot_data.items():
            windows = data['windows']
            ships = data['ships']
            fig, axes = plt.subplots(
                1, 3,
                figsize=(8, 4),   
                sharex=True
            )
            for ax, (metric, (title, unit)) in zip(axes, metrics.items()):
                for ship in ships:
                    try:
                        y = data[metric][ship]
                    except:
                        print (f'Error ploting {metric}{ship}')
                        continue
                    ax.plot(
                        windows,
                        y,
                        marker='o',
                        linewidth=1.5,
                        label=names[int(ship)-1]
                    )
                ax.margins()
                ax.set_title(title)
                ax.set_xlabel('Window (seconds)')
                ax.set_ylabel(f'{temporal} RMSE ({unit})')
                ax.grid(True, linestyle='--', alpha=0.6)
            plt.suptitle(f'{temporal} RMSE (Discard {discard_percent}%)', y=0.96)
            handles, labels = axes[0].get_legend_handles_labels()
            fig.subplots_adjust(
                left=0.06,
                right=0.99,
                top=0.85,
                bottom=0.2,   
                wspace=0.25
            )
            fig.legend(
                handles,
                labels,
                loc='lower center',
                ncol=6,
                fontsize=6,
                bbox_to_anchor=(0.5, 0.02)
            )
            
           # plt.tight_layout()
            filename = f'{temporal}_rmse_errors_discard_{discard_percent}.png'
            plt.savefig(os.path.join(output_folder, filename), dpi=600)
            plt.close()

           
    @staticmethod
    def save_csv_rmse(percentile_descarted,content, path, test_case):
        path_to_save = os.path.join(path,'results/',f'test_{test_case}_{percentile_descarted}.csv')        
        tFile = codecs.open(path_to_save, 'w', 'utf-8')
        tFile.write(content)
        tFile.close()