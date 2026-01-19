"""
体测分析服务
"""
from typing import Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.fitness_test import FitnessTest
from app.models.student import Student
from app.models.resource import InternalResource


class FitnessService:
    """体测分析服务"""
    
    # 国家学生体质健康标准（示例 - 小学四年级）
    STANDARDS = {
        'grade_4_boy': {
            'fifty_meter_run': {
                'excellent': 9.0, 'good': 10.0, 'pass': 11.5, 'fail': 13.0
            },
            'standing_long_jump': {
                'excellent': 160, 'good': 140, 'pass': 120, 'fail': 100
            },
            'one_minute_sit_ups': {
                'excellent': 40, 'good': 32, 'pass': 24, 'fail': 16
            },
            'sit_and_reach': {
                'excellent': 12.0, 'good': 8.0, 'pass': 4.0, 'fail': 0.0
            }
        },
        'grade_4_girl': {
            'fifty_meter_run': {
                'excellent': 9.5, 'good': 10.5, 'pass': 12.0, 'fail': 13.5
            },
            'standing_long_jump': {
                'excellent': 150, 'good': 130, 'pass': 110, 'fail': 90
            },
            'one_minute_sit_ups': {
                'excellent': 38, 'good': 30, 'pass': 22, 'fail': 14
            },
            'sit_and_reach': {
                'excellent': 14.0, 'good': 10.0, 'pass': 6.0, 'fail': 2.0
            }
        }
    }
    
    # 项目与身体素质映射
    QUALITY_MAP = {
        'fifty_meter_run': ['speed', 'leg_strength'],
        'standing_long_jump': ['explosive', 'leg_strength'],
        'one_minute_sit_ups': ['core_strength', 'endurance'],
        'sit_and_reach': ['flexibility'],
        'pull_ups': ['upper_strength', 'endurance'],
        'endurance_run': ['endurance', 'cardio']
    }
    
    async def get_latest_test(
        self,
        student_id: int,
        db: AsyncSession
    ) -> Optional[FitnessTest]:
        """
        获取学生最新体测数据
        
        Args:
            student_id: 学生ID
            db: 数据库会话
            
        Returns:
            体测数据
        """
        result = await db.execute(
            select(FitnessTest)
            .where(FitnessTest.student_id == student_id)
            .order_by(FitnessTest.test_date.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    def analyze_test(
        self,
        test: FitnessTest,
        grade: str = 'grade_4',
        gender: str = 'boy'
    ) -> Dict:
        """
        分析体测成绩
        
        Args:
            test: 体测数据
            grade: 年级
            gender: 性别
            
        Returns:
            分析结果
        """
        standard_key = f"{grade}_{gender}"
        standards = self.STANDARDS.get(standard_key, self.STANDARDS['grade_4_boy'])
        
        # 计算各项得分
        scores = {}
        
        if test.fifty_meter_run:
            scores['fifty_meter_run'] = self._calculate_score(
                test.fifty_meter_run,
                standards['fifty_meter_run'],
                reverse=True  # 时间越短越好
            )
        
        if test.standing_long_jump:
            scores['standing_long_jump'] = self._calculate_score(
                test.standing_long_jump,
                standards['standing_long_jump']
            )
        
        if test.one_minute_sit_ups:
            scores['one_minute_sit_ups'] = self._calculate_score(
                test.one_minute_sit_ups,
                standards['one_minute_sit_ups']
            )
        
        if test.sit_and_reach:
            scores['sit_and_reach'] = self._calculate_score(
                test.sit_and_reach,
                standards['sit_and_reach']
            )
        
        # 找出最弱和次弱项
        sorted_scores = sorted(scores.items(), key=lambda x: x[1])
        
        analysis = {
            'total_score': test.total_score,
            'scores': scores,
            'weakest': sorted_scores[0][0] if len(sorted_scores) > 0 else None,
            'weakest_score': sorted_scores[0][1] if len(sorted_scores) > 0 else None,
            'second_weakest': sorted_scores[1][0] if len(sorted_scores) > 1 else None,
            'second_weakest_score': sorted_scores[1][1] if len(sorted_scores) > 1 else None,
            'qualities_to_improve': []
        }
        
        # 确定需要提升的身体素质
        if analysis['weakest']:
            analysis['qualities_to_improve'].extend(
                self.QUALITY_MAP.get(analysis['weakest'], [])
            )
        
        if analysis['second_weakest']:
            for quality in self.QUALITY_MAP.get(analysis['second_weakest'], []):
                if quality not in analysis['qualities_to_improve']:
                    analysis['qualities_to_improve'].append(quality)
        
        return analysis
    
    def _calculate_score(
        self,
        value: float,
        standard: Dict,
        reverse: bool = False
    ) -> float:
        """
        计算单项得分
        
        Args:
            value: 实际值
            standard: 标准值
            reverse: 是否反向计算（时间类项目）
            
        Returns:
            得分（0-100）
        """
        if reverse:
            # 时间越短越好
            if value <= standard['excellent']:
                return 100
            elif value <= standard['good']:
                return 85
            elif value <= standard['pass']:
                return 60
            else:
                return 40
        else:
            # 数值越大越好
            if value >= standard['excellent']:
                return 100
            elif value >= standard['good']:
                return 85
            elif value >= standard['pass']:
                return 60
            else:
                return 40
    
    async def generate_training_plan(
        self,
        analysis: Dict,
        db: AsyncSession
    ) -> Dict:
        """
        生成训练方案
        
        Args:
            analysis: 分析结果
            db: 数据库会话
            
        Returns:
            训练方案
        """
        qualities = analysis['qualities_to_improve']
        
        if not qualities:
            return {
                'message': '您的体测成绩很好，继续保持！',
                'exercises': []
            }
        
        # 从动作库查找训练动作
        exercises = []
        
        for quality in qualities[:2]:  # 只取前两个素质
            result = await db.execute(
                select(InternalResource)
                .where(InternalResource.category == quality)
                .where(InternalResource.type == 'exercise')
                .limit(3 if quality == qualities[0] else 1)
            )
            quality_exercises = result.scalars().all()
            exercises.extend(quality_exercises)
        
        # 格式化训练方案
        plan = {
            'weakest_quality': qualities[0] if qualities else None,
            'weakest_item': analysis['weakest'],
            'exercises': [
                {
                    'title': ex.title,
                    'content': ex.content,
                    'file_url': ex.file_url
                }
                for ex in exercises
            ],
            'suggestion': self._generate_suggestion(analysis)
        }
        
        return plan
    
    def _generate_suggestion(self, analysis: Dict) -> str:
        """生成训练建议"""
        weakest = analysis.get('weakest')
        
        suggestions = {
            'fifty_meter_run': '建议加强速度和下肢力量训练，每周进行3-4次短跑练习。',
            'standing_long_jump': '建议加强爆发力和腿部力量训练，多做跳跃类练习。',
            'one_minute_sit_ups': '建议加强核心力量训练，每天坚持做仰卧起坐练习。',
            'sit_and_reach': '建议加强柔韧性训练，每天进行拉伸练习。'
        }
        
        return suggestions.get(weakest, '建议坚持锻炼，全面提升身体素质。')


# 创建全局体测服务实例
fitness_service = FitnessService()
