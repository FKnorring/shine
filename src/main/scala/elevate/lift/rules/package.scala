package elevate.lift

import elevate.core.strategies.basic.normalize
import elevate.core.strategies.predicate._
import elevate.lift.strategies.traversal._
import elevate.lift.extractors._
import elevate.core.{Failure, Lift, RewriteResult, Strategy, Success}
import elevate.lift.rules.algorithmic.untype
import lift.core._
import lift.core.types._

package object rules {

  case object betaReduction extends Strategy[Lift] {
    def apply(e: Lift): RewriteResult[Lift] = e match {
      case _apply(f, x) => lifting.liftFunExpr(f) match {
        case lifting.Reducing(lf) => Success(lf(x))
        case _ => Failure(betaReduction)
      }
      // TODO: typed
      case DepApply(f, x: Nat) => lifting.liftDepFunExpr[NatKind](f) match {
        case lifting.Reducing(lf) => Success(lf(x))
        case _ => Failure(betaReduction)
      }
      case _ => Failure(betaReduction)
    }
    override def toString = "betaReduction"
  }

  case object etaReduction extends Strategy[Lift]  {
    def apply(e: Lift): RewriteResult[Lift] = e match {
      case _lambda(x1, _apply(f, x2)) if x1 == x2 && !contains[Lift](x1).apply(f) => Success(f)
      case _ => Failure(etaReduction)
    }
    override def toString = "etaReduction"
  }

  case object etaAbstraction extends Strategy[Lift] {
    // TODO? check that `f` is a function (i.e. has a function type)
    def apply(e: Lift): RewriteResult[Lift] = e match {
      case f =>
        val x = Identifier(freshName("η"))
        Success(Lambda(x, Apply(f, x)))
    }
    override def toString = "etaAbstraction"
  }

  case object inferLift extends Strategy[Lift] {
    def apply(e: Lift): RewriteResult[Lift] = Success(infer(e))
  }

  def untypeExpr(e: Lift): Lift = normalize(untype).apply(e).get
}
