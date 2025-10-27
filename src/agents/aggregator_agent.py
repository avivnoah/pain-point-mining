class Synthesis_Agent:
    def __init__(self):
        self.report = []

    def compile_report(self, validated_pain_points):
        self.report = self.format_report(validated_pain_points)
        return self.report

    def format_report(self, validated_pain_points):
        formatted_report = []
        for point in validated_pain_points:
            formatted_report.append({
                'pain_point': point['pain_point'],
                'source': point['source'],
                'timestamp': point['timestamp']
            })
        return formatted_report