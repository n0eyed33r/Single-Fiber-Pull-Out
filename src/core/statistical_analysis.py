"""
statistical_analysis.py - Erweitertes Statistikmodul für den SFPO-Analyzer

Dieses Modul implementiert fortgeschrittene statistische Methoden:
- Bootstrap-Verfahren für kleine Stichproben
- ANOVA-Tests zum Vergleich verschiedener Messreihen
- Post-hoc-Tests und Visualisierungen
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from pathlib import Path
from typing import Dict, Any
import logging
from datetime import datetime

class StatisticalAnalyzer:
    """
    Implementiert fortgeschrittene statistische Methoden für den SFPO-Analyzer.
    Unterstützt Bootstrap-Verfahren und ANOVA-Tests.
    """

    def __init__(self, logger=None):
        """
        Initialisiert den StatisticalAnalyzer.

        Args:
            logger: Logger-Instanz für Protokollierung (optional)
        """
        self.logger = logger or logging.getLogger('SFPO_Analyzer')

        # Für Reproduzierbarkeit einen festen Seed setzen
        np.random.seed(42)

        # Einstellungen für Plots
        sns.set_style("whitegrid")
        plt.rcParams['font.size'] = 12
        plt.rcParams['axes.labelsize'] = 14
        plt.rcParams['axes.titlesize'] = 16
        plt.rcParams['xtick.labelsize'] = 12
        plt.rcParams['ytick.labelsize'] = 12

        # Für die Speicherung von Ergebnissen
        self.bootstrap_results = {}
        self.anova_results = {}

    def bootstrap_sample(self, data: np.ndarray, n_bootstrap: int = 1000) -> Dict[str, Any]:
        """
        Führt Bootstrap-Resampling für einen einzelnen Datensatz durch.

        Args:
            data: Originaldaten als NumPy-Array
            n_bootstrap: Anzahl der Bootstrap-Stichproben

        Returns:
            Dictionary mit Bootstrap-Statistiken
        """
        # Sicherheitscheck für leere oder ungültige Daten
        if data is None or len(data) == 0:
            self.logger.warning("Leerer Datensatz für Bootstrap übergeben")
            return {
                'means': np.array([]),
                'medians': np.array([]),
                'stds': np.array([]),
                'ci_mean': np.array([np.nan, np.nan]),
                'ci_median': np.array([np.nan, np.nan]),
                'ci_std': np.array([np.nan, np.nan])
            }

        # Stichprobengröße
        n = len(data)
        self.logger.info(f"Führe Bootstrap mit {n_bootstrap} Wiederholungen für {n} Datenpunkte durch")

        # Speicher für Bootstrap-Statistiken
        bootstrap_means = np.zeros(n_bootstrap)
        bootstrap_medians = np.zeros(n_bootstrap)
        bootstrap_stds = np.zeros(n_bootstrap)

        # Erzeuge n_bootstrap Stichproben mit Zurücklegen
        for i in range(n_bootstrap):
            # Ziehe zufällige Indizes mit Zurücklegen
            indices = np.random.choice(n, size=n, replace=True)

            # Erstelle Bootstrap-Stichprobe
            bootstrap_sample = data[indices]

            # Berechne und speichere Statistiken
            bootstrap_means[i] = np.mean(bootstrap_sample)
            bootstrap_medians[i] = np.median(bootstrap_sample)
            bootstrap_stds[i] = np.std(bootstrap_sample, ddof=1)  # ddof=1 für unverzerrte Schätzung

        # Berechne Konfidenzintervalle (95%)
        ci_mean = np.percentile(bootstrap_means, [2.5, 97.5])
        ci_median = np.percentile(bootstrap_medians, [2.5, 97.5])
        ci_std = np.percentile(bootstrap_stds, [2.5, 97.5])

        # Berechne auch andere Konfidenzintervalle (90%)
        ci_mean_90 = np.percentile(bootstrap_means, [5, 95])

        self.logger.info(f"Bootstrap abgeschlossen. 95% CI für Mittelwert: [{ci_mean[0]:.4f}, {ci_mean[1]:.4f}]")

        return {
            'means': bootstrap_means,
            'medians': bootstrap_medians,
            'stds': bootstrap_stds,
            'ci_mean': ci_mean,
            'ci_mean_90': ci_mean_90,
            'ci_median': ci_median,
            'ci_std': ci_std,
            'original_mean': np.mean(data),
            'original_median': np.median(data),
            'original_std': np.std(data, ddof=1)
        }

    def bootstrap_sample_for_anova(self, data: np.ndarray, target_size: int = 10, n_bootstrap: int = 1000) -> np.ndarray:
        """
        Erzeugt mit Bootstrap eine größere Stichprobe für die ANOVA.

        Args:
            data: Originaldaten als NumPy-Array
            target_size: Zielgröße der erweiterten Stichprobe
            n_bootstrap: Anzahl der Bootstrap-Stichproben

        Returns:
            Erweiterte Stichprobe der Zielgröße
        """
        # Sicherheitscheck für leere oder ungültige Daten
        if data is None or len(data) == 0:
            self.logger.warning("Leerer Datensatz für Bootstrap-ANOVA übergeben")
            return np.array([])

        # Stichprobengröße
        n = len(data)

        # Erzeuge eine große Menge an Bootstrap-Samples
        all_samples = np.zeros(n_bootstrap * n)

        # Erzeuge n_bootstrap Stichproben mit Zurücklegen
        for i in range(n_bootstrap):
            # Ziehe zufällige Indizes mit Zurücklegen
            indices = np.random.choice(n, size=n, replace=True)

            # Erstelle Bootstrap-Stichprobe und speichere sie
            all_samples[i * n:(i + 1) * n] = data[indices]

        # Wähle zufällig target_size Elemente aus allen Samples
        if len(all_samples) >= target_size:
            extended_sample = np.random.choice(all_samples, size=target_size, replace=False)
        else:
            # Wenn nicht genug Samples vorhanden sind, verwende alle und ergänze durch Ziehen mit Zurücklegen
            extended_sample = np.random.choice(all_samples, size=target_size, replace=True)

        self.logger.info(f"Bootstrap für ANOVA: Datensatz von {n} auf {target_size} Datenpunkte erweitert")
        return extended_sample

    def perform_bootstrap_analysis(self, data_dict: Dict[str, np.ndarray], output_folder: Path = None) -> Dict[
        str, Dict[str, Any]]:
        """
        Führt eine vollständige Bootstrap-Analyse für mehrere Datensätze durch.

        Args:
            data_dict: Dictionary mit Messnamen als Schlüssel und Daten als Werte
            output_folder: Ordner zum Speichern der Ergebnisplots (optional)

        Returns:
            Dictionary mit Bootstrap-Ergebnissen für jeden Datensatz
        """
        results = {}

        for name, data in data_dict.items():
            self.logger.info(f"Starte Bootstrap-Analyse für {name}")

            # Überprüfe, ob Daten vorhanden sind
            if data is None or len(data) == 0:
                self.logger.warning(f"Keine Daten für {name}, überspringe Bootstrap-Analyse")
                continue

            # Führe Bootstrap durch
            bootstrap_result = self.bootstrap_sample(data)
            results[name] = bootstrap_result

            # Erstelle und speichere Visualisierung, wenn output_folder angegeben ist
            if output_folder is not None:
                self.visualize_bootstrap(name, bootstrap_result, output_folder)

        # Speichere Ergebnisse für spätere Verwendung
        self.bootstrap_results = results

        return results

    def visualize_bootstrap(self, name: str, results: Dict[str, Any], output_folder: Path) -> None:
        """
        Visualisiert die Ergebnisse einer Bootstrap-Analyse.

        Args:
            name: Name des Datensatzes
            results: Bootstrap-Ergebnisse als Dictionary
            output_folder: Ordner zum Speichern der Plots
        """
        # Stelle sicher, dass der Ausgabeordner existiert
        output_folder.mkdir(exist_ok=True, parents=True)

        # Erstelle Plot
        plt.figure(figsize=(12, 8))

        # Histogramm der Bootstrap-Mittelwerte
        plt.hist(results['means'], bins=30, alpha=0.7, color='blue', density=True)

        # Vertikale Linien für Original und Konfidenzintervalle
        plt.axvline(results['original_mean'], color='red', linestyle='dashed', linewidth=2,
                    label=f'Originaler Mittelwert: {results["original_mean"]:.4f}')
        plt.axvline(results['ci_mean'][0], color='green', linestyle='dashed', linewidth=2,
                    label=f'95% CI Untergrenze: {results["ci_mean"][0]:.4f}')
        plt.axvline(results['ci_mean'][1], color='green', linestyle='dashed', linewidth=2,
                    label=f'95% CI Obergrenze: {results["ci_mean"][1]:.4f}')

        # Beschriftung und Formatierung
        plt.title(f'Bootstrap-Verteilung der Mittelwerte: {name}', fontsize=16)
        plt.xlabel('Mittelwert', fontsize=14)
        plt.ylabel('Dichte', fontsize=14)
        plt.legend(fontsize=12)
        plt.grid(True, alpha=0.3)

        # Füge Informationstext hinzu
        info_text = (
            f"Originaler Mittelwert: {results['original_mean']:.4f}\n"
            f"Originale Std: {results['original_std']:.4f}\n"
            f"Bootstrap-Mittelwert: {np.mean(results['means']):.4f}\n"
            f"95% CI: [{results['ci_mean'][0]:.4f}, {results['ci_mean'][1]:.4f}]"
        )
        plt.figtext(0.15, 0.80, info_text, fontsize=12,
                    bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))

        # Speichere den Plot
        plt.tight_layout()
        out_path = output_folder / f"bootstrap_{name}.png"
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close()

        self.logger.info(f"Bootstrap-Plot für {name} gespeichert: {out_path}")

    def perform_anova(self,
                      data_dict: Dict[str, np.ndarray],
                      target_size: int = 10,
                      output_folder: Path = None,
                      variable_name: str = "Messwert") -> Dict[str, Any]:
        """
        Führt eine ANOVA-Analyse mit Bootstrap-erweiterten Stichproben durch.

        Args:
            data_dict: Dictionary mit Gruppennamen als Schlüssel und Daten als Werte
            target_size: Zielgröße für jede Gruppe nach Bootstrap
            output_folder: Ordner zum Speichern der Ergebnisplots (optional)
            variable_name: Name der abhängigen Variable für Beschriftungen

        Returns:
            Dictionary mit ANOVA-Ergebnissen
        """
        # Überprüfe, ob genügend Gruppen vorhanden sind
        if len(data_dict) < 2:
            self.logger.warning(f"Mindestens 2 Gruppen für ANOVA benötigt, aber nur {len(data_dict)} bereitgestellt")
            return {'error': 'Zu wenige Gruppen für ANOVA'}

        self.logger.info(f"Starte ANOVA-Analyse für Variable '{variable_name}' mit {len(data_dict)} Gruppen")

        # Erweitere jede Gruppe mit Bootstrap
        extended_data = {}
        for name, data in data_dict.items():
            # Überprüfe, ob Daten vorhanden sind
            if data is None or len(data) == 0:
                self.logger.warning(f"Keine Daten für Gruppe '{name}', überspringe")
                continue

            # Erweitere Daten mit Bootstrap
            extended_data[name] = self.bootstrap_sample_for_anova(data, target_size)

        # Überprüfe, ob nach der Filterung noch genügend Gruppen übrig sind
        if len(extended_data) < 2:
            self.logger.warning("Nach der Datenprüfung verbleiben weniger als 2 Gruppen für ANOVA")
            return {'error': 'Unzureichende Daten für ANOVA nach Filterung'}

        # Erstelle DataFrame für ANOVA
        data_for_df = []
        group_labels = []

        for name, data in extended_data.items():
            data_for_df.append(data)
            group_labels.extend([name] * len(data))

        # Sammle alle Daten in einen Array
        all_data = np.concatenate(list(extended_data.values()))

        # Erstelle DataFrame
        df = pd.DataFrame({
            'value': all_data,
            'group': group_labels
        })

        # Führe One-Way ANOVA durch
        try:
            # Erstelle das Modell
            model = ols('value ~ group', data=df).fit()
            anova_table = sm.stats.anova_lm(model, typ=2)

            # Residuen für Annahmentests
            residuals = model.resid
            fitted_values = model.fittedvalues

            # Normalitätstest
            shapiro_test = stats.shapiro(residuals)

            # Homogenitätstest der Varianzen (Levene-Test)
            # Vorbereitung der Daten für den Levene-Test
            groups_for_levene = [group_data for group_data in extended_data.values()]
            levene_test = stats.levene(*groups_for_levene)

            # Berechne Effektgröße (Eta-Quadrat)
            SST = ((df['value'] - df['value'].mean()) ** 2).sum()
            SSE = ((residuals) ** 2).sum()
            eta_squared = (SST - SSE) / SST

            # Post-hoc-Test, wenn ANOVA signifikant ist
            tukey_results = None
            if anova_table.loc['group', 'PR(>F)'] < 0.05:
                self.logger.info("ANOVA ist signifikant. Führe Tukey HSD Post-hoc-Test durch")
                tukey = pairwise_tukeyhsd(endog=df['value'], groups=df['group'], alpha=0.05)
                tukey_results = tukey

            # Ergebnisse in Dictionary speichern
            results = {
                'anova_table': anova_table,
                'shapiro_test': shapiro_test,
                'levene_test': levene_test,
                'eta_squared': eta_squared,
                'model': model,
                'residuals': residuals,
                'fitted_values': fitted_values,
                'tukey_results': tukey_results,
                'df': df
            }

            # Visualisiere die Ergebnisse, wenn output_folder angegeben ist
            if output_folder is not None:
                self.visualize_anova_results(results, variable_name, output_folder)

            # Speichere Ergebnisse für spätere Verwendung
            self.anova_results[variable_name] = results

            self.logger.info(f"ANOVA-Analyse für '{variable_name}' abgeschlossen.")
            return results

        except Exception as e:
            self.logger.error(f"Fehler bei ANOVA-Analyse: {str(e)}")
            return {'error': str(e)}

    def visualize_anova_results(self, results: Dict[str, Any], variable_name: str, output_folder: Path) -> None:
        """
        Visualisiert die Ergebnisse einer ANOVA-Analyse.

        Args:
            results: Dictionary mit ANOVA-Ergebnissen
            variable_name: Name der abhängigen Variable für Beschriftungen
            output_folder: Ordner zum Speichern der Plots
        """
        # Stelle sicher, dass der Ausgabeordner existiert
        output_folder.mkdir(exist_ok=True, parents=True)

        # Erstelle Boxplot der Gruppen
        plt.figure(figsize=(12, 8))
        sns.boxplot(x='group', y='value', data=results['df'])
        sns.stripplot(x='group', y='value', data=results['df'], color='black', size=4, alpha=0.7)

        plt.title(f'Vergleich der Gruppen: {variable_name}', fontsize=16)
        plt.xlabel('Messreihe', fontsize=14)
        plt.ylabel(variable_name, fontsize=14)
        plt.grid(True, alpha=0.3)

        # Füge ANOVA-Ergebnisse als Text hinzu
        anova_p = results['anova_table'].loc['group', 'PR(>F)']
        f_value = results['anova_table'].loc['group', 'F']

        # Formatiere p-Wert
        if anova_p < 0.001:
            p_text = "p < 0.001"
        else:
            p_text = f"p = {anova_p:.3f}"

        plt.figtext(0.15, 0.90, f"ANOVA: F = {f_value:.2f}, {p_text}", fontsize=12,
                   bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))

        # Speichere den Plot
        out_path = output_folder / f"anova_boxplot_{variable_name}.png"
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close()

        # Erstelle Plots für die ANOVA-Annahmen
        plt.figure(figsize=(14, 6))

        # Residuen vs. Fitted Values Plot
        plt.subplot(1, 2, 1)
        plt.scatter(results['fitted_values'], results['residuals'])
        plt.axhline(y=0, color='red', linestyle='--')
        plt.title('Residuen vs. Fitted Values')
        plt.xlabel('Fitted Values')
        plt.ylabel('Residuen')
        plt.grid(True, alpha=0.3)

        # QQ-Plot der Residuen
        plt.subplot(1, 2, 2)
        stats.probplot(results['residuals'], dist="norm", plot=plt)
        plt.title('Q-Q Plot der Residuen')
        plt.grid(True, alpha=0.3)

        # Speichere den Plot
        plt.tight_layout()
        out_path = output_folder / f"anova_assumptions_{variable_name}.png"
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close()

        # Wenn Tukey-Post-hoc-Test durchgeführt wurde, zeige Ergebnisse
        if results['tukey_results'] is not None:
            # Erstelle einen Dataframe aus den Tukey-Ergebnissen
            tukey = results['tukey_results']
            tukey_df = pd.DataFrame(data=tukey._results_table.data[1:],
                                  columns=tukey._results_table.data[0])

            # Plotte die Ergebnisse
            plt.figure(figsize=(10, 6))
            sns.barplot(x='group1', y='meandiff', hue='reject', data=tukey_df)
            plt.axhline(y=0, color='red', linestyle='--')
            plt.title(f'Tukey HSD Post-hoc-Test: {variable_name}', fontsize=16)
            plt.xlabel('Gruppenvergleich', fontsize=14)
            plt.ylabel('Mittlere Differenz', fontsize=14)
            plt.legend(title='Signifikant (α=0.05)')
            plt.grid(True, alpha=0.3)

            # Speichere den Plot
            plt.tight_layout()
            out_path = output_folder / f"anova_posthoc_{variable_name}.png"
            plt.savefig(out_path, dpi=300, bbox_inches='tight')
            plt.close()

        self.logger.info(f"ANOVA-Plots für {variable_name} gespeichert in {output_folder}")

    def compare_groups(self,
                       analyzer_dict: Dict[str, Any],
                       output_folder: Path,
                       bootstrap_n: int = 1000,
                       anova_target_size: int = 10) -> Dict[str, Dict[str, Any]]:
        """
        Führt eine vollständige statistische Analyse für mehrere Messreihen durch.

        Args:
            analyzer_dict: Dictionary mit Messreihennamen und MeasurementAnalyzer-Instanzen
            output_folder: Ordner zum Speichern der Ergebnisse
            bootstrap_n: Anzahl der Bootstrap-Stichproben
            anova_target_size: Zielgröße für jede Gruppe nach Bootstrap für ANOVA

        Returns:
            Dictionary mit allen Analyseergebnissen
        """
        # Stelle sicher, dass der Ausgabeordner existiert
        output_folder.mkdir(exist_ok=True, parents=True)

        # Statistik-Unterordner erstellen
        stats_folder = output_folder / "statistical_analysis"
        bootstrap_folder = stats_folder / "bootstrap"
        anova_folder = stats_folder / "anova"

        for folder in [stats_folder, bootstrap_folder, anova_folder]:
            folder.mkdir(exist_ok=True, parents=True)

        self.logger.info(f"Starte statistische Analyse für {len(analyzer_dict)} Messreihen")

        # Ergebnisdictionary
        results = {
            'bootstrap': {},
            'anova': {}
        }

        # Extrahiere Daten für verschiedene Messgrößen
        f_max_data = {}
        work_data = {}
        ifss_data = {}

        for name, analyzer in analyzer_dict.items():
            # Extrahiere F_max-Werte
            if hasattr(analyzer, 'max_forces_data') and analyzer.max_forces_data:
                f_max_data[name] = np.array(analyzer.max_forces_data)

            # Extrahiere Arbeitswerte
            if hasattr(analyzer, 'works') and analyzer.works:
                work_data[name] = np.array(analyzer.works)

            # Extrahiere IFSS-Werte
            if hasattr(analyzer, 'ifssvalues') and analyzer.ifssvalues:
                # Filtere ungültige Werte (z.B. 0)
                valid_ifss = [val for val in analyzer.ifssvalues if val > 0]
                if valid_ifss:
                    ifss_data[name] = np.array(valid_ifss)

        # 1. Bootstrap-Analyse für jede Messgröße und jede Messreihe
        self.logger.info("Führe Bootstrap-Analysen durch...")

        # F_max Bootstrap
        if f_max_data:
            results['bootstrap']['F_max'] = self.perform_bootstrap_analysis(
                f_max_data, bootstrap_folder)

        # Arbeit Bootstrap
        if work_data:
            results['bootstrap']['Arbeit'] = self.perform_bootstrap_analysis(
                work_data, bootstrap_folder)

        # IFSS Bootstrap
        if ifss_data:
            results['bootstrap']['IFSS'] = self.perform_bootstrap_analysis(
                ifss_data, bootstrap_folder)

        # 2. ANOVA für jede Messgröße, wenn mindestens 2 Messreihen vorhanden sind
        self.logger.info("Führe ANOVA-Analysen durch...")

        # F_max ANOVA
        if len(f_max_data) >= 2:
            results['anova']['F_max'] = self.perform_anova(
                f_max_data, anova_target_size, anova_folder, "F_max [N]")

        # Arbeit ANOVA
        if len(work_data) >= 2:
            results['anova']['Arbeit'] = self.perform_anova(
                work_data, anova_target_size, anova_folder, "Arbeit [µJ]")

        # IFSS ANOVA
        if len(ifss_data) >= 2:
            results['anova']['IFSS'] = self.perform_anova(
                ifss_data, anova_target_size, anova_folder, "IFSS [MPa]")

        # 3. Erstelle Zusammenfassungsbericht
        self.create_summary_report(results, stats_folder)

        self.logger.info("Statistische Analyse abgeschlossen")
        return results

    def create_summary_report(self, results: Dict[str, Dict[str, Any]], output_folder: Path) -> None:
        """
        Erstellt einen Zusammenfassungsbericht der statistischen Analysen.

        Args:
            results: Dictionary mit allen Analyseergebnissen
            output_folder: Ordner zum Speichern des Berichts
        """
        report_path = output_folder / "statistische_Zusammenfassung.txt"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=== SFPO-Analyzer: Statistische Auswertung ===\n\n")
            f.write(f"Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n\n")

            # 1. Bootstrap-Ergebnisse
            f.write("=== BOOTSTRAP-ANALYSEN ===\n\n")

            for var_name, bootstrap_results in results['bootstrap'].items():
                f.write(f"--- {var_name} ---\n")

                for group_name, group_results in bootstrap_results.items():
                    orig_mean = group_results['original_mean']
                    ci_lower, ci_upper = group_results['ci_mean']

                    f.write(f"{group_name}:\n")
                    f.write(f"  Originaler Mittelwert: {orig_mean:.4f}\n")
                    f.write(f"  95% Konfidenzintervall: [{ci_lower:.4f}, {ci_upper:.4f}]\n")
                    f.write(f"  Stichprobengröße: {len(group_results['means']) // 1000}\n\n")

            # 2. ANOVA-Ergebnisse
            f.write("\n=== ANOVA-ANALYSEN ===\n\n")

            for var_name, anova_results in results['anova'].items():
                f.write(f"--- {var_name} ---\n")

                if 'error' in anova_results:
                    f.write(f"Fehler bei der ANOVA: {anova_results['error']}\n\n")
                    continue

                # ANOVA-Tabelle
                anova_table = anova_results['anova_table']
                f_value = anova_table.loc['group', 'F']
                p_value = anova_table.loc['group', 'PR(>F)']

                f.write(f"F-Wert: {f_value:.4f}\n")
                f.write(f"p-Wert: {p_value:.4f}\n")
                f.write(f"Signifikant: {'Ja' if p_value < 0.05 else 'Nein'}\n")
                f.write(f"Effektgröße (Eta²): {anova_results['eta_squared']:.4f}\n\n")

                # Annahmentests
                shapiro_w, shapiro_p = anova_results['shapiro_test']
                levene_w, levene_p = anova_results['levene_test']

                f.write("Annahmentests:\n")
                f.write(f"  Normalitätstest (Shapiro-Wilk): W = {shapiro_w:.4f}, p = {shapiro_p:.4f}\n")
                f.write(f"  {'✓' if shapiro_p > 0.05 else '✗'} Residuen sind normalverteilt\n")
                f.write(f"  Varianztest (Levene): W = {levene_w:.4f}, p = {levene_p:.4f}\n")
                f.write(f"  {'✓' if levene_p > 0.05 else '✗'} Varianzen sind homogen\n\n")

                # Post-hoc-Test, wenn vorhanden
                if anova_results['tukey_results'] is not None:
                    f.write("Post-hoc-Test (Tukey HSD):\n")
                    tukey = anova_results['tukey_results']

                    # Erstelle einen Dataframe aus den Tukey-Ergebnissen
                    tukey_df = pd.DataFrame(data=tukey._results_table.data[1:],
                                          columns=tukey._results_table.data[0])

                    for _, row in tukey_df.iterrows():
                        group1 = row['group1']
                        group2 = row['group2']
                        meandiff = row['meandiff']
                        p_adj = row['p-adj']
                        reject = row['reject']

                        f.write(f"  {group1} vs. {group2}: Differenz = {meandiff:.4f}, p = {p_adj:.4f}")
                        f.write(f" {'*' if reject else ''}\n")

                    f.write("\n  * signifikant bei α=0.05\n\n")

            f.write("\n=== ENDE DES BERICHTS ===\n")

        self.logger.info(f"Zusammenfassungsbericht erstellt: {report_path}")

        # Erstelle auch eine Excel-Version des Berichts für einfachere Weiterverarbeitung
        excel_path = output_folder / "statistische_Zusammenfassung.xlsx"

        with pd.ExcelWriter(excel_path) as writer:
            # Bootstrap-Ergebnisse
            bootstrap_data = []

            for var_name, bootstrap_results in results['bootstrap'].items():
                for group_name, group_results in bootstrap_results.items():
                    orig_mean = group_results['original_mean']
                    ci_lower, ci_upper = group_results['ci_mean']

                    bootstrap_data.append({
                        'Variable': var_name,
                        'Gruppe': group_name,
                        'Mittelwert': orig_mean,
                        'CI_Untergrenze': ci_lower,
                        'CI_Obergrenze': ci_upper,
                        'Stichprobengröße': len(group_results['means']) // 1000
                    })

            if bootstrap_data:
                bootstrap_df = pd.DataFrame(bootstrap_data)
                bootstrap_df.to_excel(writer, sheet_name='Bootstrap', index=False)

            # ANOVA-Ergebnisse
            anova_data = []

            for var_name, anova_results in results['anova'].items():
                if 'error' in anova_results:
                    continue

                anova_table = anova_results['anova_table']
                f_value = anova_table.loc['group', 'F']
                p_value = anova_table.loc['group', 'PR(>F)']

                anova_data.append({
                    'Variable': var_name,
                    'F_Wert': f_value,
                    'p_Wert': p_value,
                    'Signifikant': p_value < 0.05,
                    'Eta_Quadrat': anova_results['eta_squared'],
                    'Shapiro_W': anova_results['shapiro_test'][0],
                    'Shapiro_p': anova_results['shapiro_test'][1],
                    'Levene_W': anova_results['levene_test'][0],
                    'Levene_p': anova_results['levene_test'][1]
                })

            if anova_data:
                anova_df = pd.DataFrame(anova_data)
                anova_df.to_excel(writer, sheet_name='ANOVA', index=False)

            # Post-hoc-Tests
            posthoc_data = []

            for var_name, anova_results in results['anova'].items():
                if 'error' in anova_results or anova_results['tukey_results'] is None:
                    continue

                tukey = anova_results['tukey_results']
                tukey_df = pd.DataFrame(data=tukey._results_table.data[1:],
                                      columns=tukey._results_table.data[0])

                for _, row in tukey_df.iterrows():
                    posthoc_data.append({
                        'Variable': var_name,
                        'Gruppe1': row['group1'],
                        'Gruppe2': row['group2'],
                        'Mittlere_Differenz': row['meandiff'],
                        'p_Wert': row['p-adj'],
                        'Signifikant': row['reject']
                    })

            if posthoc_data:
                posthoc_df = pd.DataFrame(posthoc_data)
                posthoc_df.to_excel(writer, sheet_name='Post-hoc', index=False)

        self.logger.info(f"Excel-Zusammenfassung erstellt: {excel_path}")